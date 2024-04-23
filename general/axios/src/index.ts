import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from "axios";
import { Handler, Outputs } from "./types";
import * as fs from "fs";
import * as path from "path";

// Helper function to generate a unique file name.
function generateFileName(url: string): string {
  const datePrefix = new Date().toISOString().replace(/[:.]/g, "-");
  const urlHash = Buffer.from(url).toString("hex").substring(0, 6);
  return `download-${datePrefix}-${urlHash}.tmp`;
}

async function axiosWrapper(
  method = "GET",
  url: string,
  data: string | NodeJS.ReadableStream | Buffer,
  headers = {},
  params = {},
  streamToFile = false,
  dataFromFile = ""
): Promise<Outputs> {
  let requestData: string | NodeJS.ReadableStream | Buffer = data;

  // If data is provided from a file, create a read stream
  if (dataFromFile) {
    requestData = fs.createReadStream(dataFromFile);
  } else if (typeof data === "string") {
    // If data is a string, convert it to a Buffer
    requestData = Buffer.from(data);
  }

  const defaultHeaders = {
    ...headers,
  };

  const options: AxiosRequestConfig = {
    method,
    url,
    headers: defaultHeaders,
    data: requestData,
    params,
    responseType: streamToFile ? "stream" : "json",
  };

  console.log("options:", options);

  return axios(options)
    .then((res: AxiosResponse) => {
      if (streamToFile) {
        const fileName = generateFileName(url);
        const filePath = path.join(__dirname, fileName);
        const writer = fs.createWriteStream(filePath);

        return new Promise<Outputs>((resolve, reject) => {
          res.data.pipe(writer);
          writer.on("finish", () => {
            // Close the writer stream when finished writing
            writer.close();
            resolve({
              response: {
                status: res.status,
                statusText: res.statusText,
                headers: res.headers,
                // @ts-ignore
                file: filePath, // Return the path of the downloaded file
              },
            });
          });
          writer.on("error", (err) => {
            // Close the writer stream and reject with the error
            writer.close();
            reject(err);
          });
        });
      } else {
        return {
          response: {
            status: res.status,
            statusText: res.statusText,
            headers: res.headers,
            data: res.data,
            config: res.config,
          },
        };
      }
    })
    .catch((err: AxiosError) => {
      if (err.response) {
        console.warn("err.response.data:", err.response.data);
        console.warn("err.response.status:", err.response.status);
        console.warn("err.response.headers:", err.response.headers);
      }
      console.log(err.message);
      return { error: err };
    }) as Outputs;
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
