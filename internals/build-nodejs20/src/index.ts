import fs from "fs";
import { execSync } from "child_process";

const handler = async (inputs) => {
  const { code: codePath } = inputs;

  // Assuming codePath is a directory containing package.json
  try {
    // Synchronously execute npm install in the codePath directory
    console.log("npm installing in ", codePath);
    const tmpNpmDir = "/tmp/npm-tmp";
    fs.mkdirSync(tmpNpmDir, { recursive: true });
    // install only production dependencies
    execSync(
      "npm install --only=production --ignore-scripts --no-audit --no-fund --cache /tmp/npm-cache",
      {
        cwd: codePath,
        stdio: "inherit",
        env: {
          ...process.env,
          // Override all npm-related locations
          npm_config_cache: "/tmp/npm-cache",
          npm_config_tmp: "/tmp/npm-tmp",
          npm_config_prefix: "/tmp/npm-prefix",
          HOME: "/tmp", // for .npmrc fallback
        },
      }
    );

    // remove package.json and package-lock.json since they cause when executing
    if (fs.existsSync(`${codePath}/package-lock.json`))
      fs.unlinkSync(`${codePath}/package-lock.json`);
    if (fs.existsSync(`${codePath}/package.json`))
      fs.unlinkSync(`${codePath}/package.json`);
    console.log("NPM modules installed successfully.");
  } catch (error) {
    console.error("Error installing NPM modules:", error);
    return { code: codePath };
  }

  return { code: codePath };
};

export { handler };
