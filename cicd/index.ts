import crypto from "crypto";
import archiver from "archiver";
import { PluginManager } from "live-plugin-manager";
import Ajv, { Schema } from "ajv";
import { createGenerator } from "ts-json-schema-generator";

const TS_BUILD_DIR = "dist";
const INTERFACE_TYPES_FILENAME = "types.ts";
class Test {

  create() {
    this.logger.debug("create function");
    // Check if remotely exists and begin of local build
    // if (!lambdaGetResponse && !fs.existsSync(`${this.gitModule.repoFullPath}/node_modules`)) {
    await this.installPackagesAndCreateLayer();
    this.createTsConfig();
    // is needed for validation later
    this.logger.info("Building code")
    // Needs to be after guards creation
    await this.buildCode();
    this.logger.info("code built")
    await this.exec(`ls ${this.gitModule.repoFullPath}`, "ls repo");
    await this.exec(
      `ls ${this.gitModule.repoFullPath}/${TS_BUILD_DIR}`,
      "ls dist"
    );

    const dependencyLayerArn = await this.publishLayer();
    const resultZipPath = `${this.gitModule.repoFullPath}/code.zip`;
    await this.zip(
      `${this.gitModule.repoFullPath}/${TS_BUILD_DIR}`,
      resultZipPath
    );
    this.logger.info(`uploading code to bucket..`);
    await this.s3Client.send(
      new PutObjectCommand({
        Bucket: "edurata-customer-functions" + this.suffix,
        Key: this.id,
        Body: fs.readFileSync(resultZipPath),
      })
    );
    this.logger.info(`Uploaded!`)
  }
    createTsConfig() {
        const tsConfig = {
          compilerOptions: {
            lib: ["es2020", "dom"],
            module: "commonjs",
            target: "es2020",
            strict: false,
            esModuleInterop: true,
            skipLibCheck: true,
            allowJs: true,
            forceConsistentCasingInFileNames: true,
            allowSyntheticDefaultImports: true,
            //   moduleResolution: "node",
            sourceMap: false,
            baseUrl: "./",
            outDir: TS_BUILD_DIR,
          },
          include: ["src/**/*", "index.ts"],
        };
        fs.writeFileSync(
          `${this.gitModule.repoFullPath}/tsconfig.json`,
          JSON.stringify(tsConfig)
        );
      }
    
      // build function code that should be used in statemachine
      async buildCode() {
        await this.exec(
          `cd ${this.gitModule.repoFullPath} && node ${this.pathNodeModules}/typescript/lib/tsc.js`,
          "Typescript compile"
        );
      }
    
      async installPackagesAndCreateLayer() {
        const credsWrapper = async (key: string, value: string) => {
          if (value.includes("ssh://")) {
            throw Error("Pulling over ssh not supported yet. use https");
          }
          if (value.includes("https://")) {
            const rx = /https:\/\/(.*)@/g;
            const githubUser = rx.exec(value)?.at(1);
            if (!githubUser) {
              throw Error(
                `No github user found for package ${key}. Add it like https://username@github.com... and specify an access token in the edurata UI.`
              );
            }
            const secret = await appSyncRequest(getSecret, {
              id: githubUser, // TODO special naming scheme to differnentiate git credentials from other secrets
              owner: this.userId,
            });
            if (!secret) {
              throw Error(`No secret found for ${key}. Add it in the UI.`);
            }
            const replacedValue = value.replace(
              `${githubUser}@`,
              `${githubUser}:${secret}@`
            );
            return manager.install(key, replacedValue);
          }
          return manager.install(key, value);
        };
        const nodejsPath = `${this.gitModule.repoFullPath}/nodejs`;
        if (!fs.existsSync(`${this.gitModule.repoFullPath}/package.json`)) {
          return this.logger.info("No package.json found, skipping..");
        }
        fs.mkdirSync(nodejsPath, { recursive: true });
        fs.mkdirSync(`${this.gitModule.repoFullPath}/node_modules`, {
          recursive: true,
        });
        const manager = new PluginManager({
          // cwd: ,
          pluginsPath: `${this.gitModule.repoFullPath}/node_modules`,
        });
        const packageJson = JSON.parse(
          fs.readFileSync(`${this.gitModule.repoFullPath}/package.json`, "utf8")
        );
        const allPackages = await Promise.all(
          Object.entries({
            "@types/node": "^17.0.21",
            ...packageJson.dependencies,
          }).map(([key, value]) => credsWrapper(key, value as string))
        );
        this.logger.info("Installed " + allPackages.length + " packages");
        // node ${this.pathNodeModules}/yarn/bin/yarn.js install @types/node &&
        await this.exec(
          `cd ${this.gitModule.repoFullPath} && cp -r ${this.gitModule.repoFullPath}/node_modules ${nodejsPath}`,
          "npm install"
        );
      }
    
      // TODO check here if orig size above limit of 150mb
      async zip(source: string, destination: string) {
        const stream = fs.createWriteStream(destination);
        const archive = archiver("zip", { zlib: { level: 9 } });
        this.logger.info("Zipping file at " + source);
        return new Promise((resolve, reject) => {
          archive
            .directory(source, false)
            .on("error", (err) => reject(err))
            .pipe(stream);
          stream.on("close", () => resolve(true));
          archive.finalize();
        });
      }
    
      // create layer if not existant, returns name of layer
      async publishLayer() {
        if (!fs.existsSync(`${this.gitModule.repoFullPath}/package.json`)) {
          const packageJson = JSON.parse(
            fs.readFileSync(`${this.gitModule.repoFullPath}/package.json`, "utf8")
          );
    
          const packageEntriesString = Object.entries(packageJson.dependencies)
            .sort((a, b) => (a < b ? -1 : 1))
            .reduce((prev, cur, index) => `${prev}.${cur[0]}_${cur[1]}`, "");
    
          if (packageEntriesString.length) {
            const packageEntriesStringHashed = crypto
              .createHash("md5")
              .update(packageEntriesString)
              .digest("hex");
            const LayerName = `arn:aws:lambda:eu-central-1:${this.accountId}:layer:${packageEntriesStringHashed}`;
            const listLayersResponse: any = await this.lambdaClient
              .send(
                new ListLayerVersionsCommand({
                  LayerName,
                })
              )
              .catch((e) =>
                this.logger.alert(`error during listing layers ${JSON.stringify(e)}`)
              );
            if (
              !listLayersResponse?.LayerVersions ||
              (listLayersResponse?.LayerVersions &&
                listLayersResponse?.LayerVersions.length === 0)
            ) {
              this.logger.info(
                `Couldn't find layer version for ${packageEntriesString}, creating new one..`
              );
              await this.zip(
                `${this.gitModule.repoFullPath}/nodejs`,
                `${this.gitModule.repoFullPath}/layer.zip`
              );
              await this.lambdaClient
                .send(
                  new PublishLayerVersionCommand({
                    LayerName,
                    Content: {
                      ZipFile: fs.readFileSync(
                        `${this.gitModule.repoFullPath}/layer.zip`
                      ),
                    },
                  })
                )
                .catch((e) =>
                  this.logger.alert(`error during pushing layer ${JSON.stringify(e)}`)
                );
            }
            const highestVersion = listLayersResponse?.LayerVersions?.length
              ? listLayersResponse?.LayerVersions?.sort(
                  (a, b) => (b.Version ?? 0) - (a.Version ?? 0)
                )[0].Version
              : 1;
    
            return `${LayerName}:${highestVersion}`;
          }
        }
      }
    
}
