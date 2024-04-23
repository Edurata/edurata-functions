import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from "axios";
import { Handler, Outputs } from "./types";
import * as fs from "fs";
import * as path from "path";
import { Readable } from "stream";

// Helper function to generate a unique file name.
function generateFileName(url: string): string {
  const datePrefix = new Date().toISOString().replace(/[:.]/g, "-");
  const urlHash = Buffer.from(url).toString("hex").substring(0, 6);
  return `download-${datePrefix}-${urlHash}.tmp`;
}

async function axiosWrapper(
  method = "GET",
  url: string,
  data: any,
  headers: any = {},
  params: any = {},
  streamToFile = false,
  dataFromFile = ""
): Promise<Outputs> {
  const defaultHeaders = {
    ...headers,
  };

  const options: AxiosRequestConfig = {
    method,
    url,
    headers: defaultHeaders,
    params,
    responseType: streamToFile ? "stream" : "json",
  };

  console.log("options:", options);

  try {
    const response: AxiosResponse =
      dataFromFile && streamToFile
        ? await axios({
            ...options,
            data: fs.createReadStream(dataFromFile),
          })
        : await axios({
            ...options,
            data:
              typeof data === "string" || data instanceof Buffer
                ? data
                : JSON.stringify(data),
          });

    if (streamToFile) {
      const fileName = generateFileName(url);
      const filePath = path.join(__dirname, fileName);
      const writer = fs.createWriteStream(filePath);
      response.data.pipe(writer);

      return new Promise<Outputs>((resolve, reject) => {
        writer.on("finish", () => {
          writer.close();
          resolve({
            response: {
              status: response.status,
              statusText: response.statusText,
              headers: response.headers,
              // @ts-ignore
              file: filePath,
            },
          });
        });
        writer.on("error", (err) => {
          reject(err);
        });
      });
    } else {
      return {
        response: {
          status: response.status,
          statusText: response.statusText,
          headers: response.headers,
          data: response.data,
          config: response.config,
        },
      };
    }
  } catch (error) {
    return { error };
  }
}

const handler: Handler = async (inputs) => {
  const { method, url, data, headers, params, streamToFile, dataFromFile } =
    inputs;
  return await axiosWrapper(
    method,
    url,
    data,
    headers,
    params,
    streamToFile,
    dataFromFile
  );
};

export { handler };
