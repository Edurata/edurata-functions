import axios, { AxiosError, AxiosRequestConfig } from "axios";
import { Handler, Outputs } from "./types";
import * as fs from "fs";
import * as path from "path";
const readFile = require("util").promisify(fs.readFile);
// Helper function to generate a unique file name.
function generateFileName(url: string): string {
  const datePrefix = new Date().toISOString().replace(/[:.]/g, "-");
  const urlHash = Buffer.from(url).toString("hex").substring(0, 6);
  return `download-${datePrefix}-${urlHash}.tmp`;
}

async function axiosWrapper(
  method = "GET",
  url,
  data,
  headers = {},
  params = {},
  streamToFile = false,
  dataFromFile = ""
): Promise<Outputs> {
  let dataToSend = data;
  const defaultHeaders = {
    ...headers,
  };

  if (dataFromFile) {
    dataToSend = await readFile(dataFromFile);
  }

  const options: AxiosRequestConfig = {
    method,
    url,
    headers: defaultHeaders,
    data: dataToSend,
    params,
    responseType: streamToFile ? "stream" : "json",
  };

  console.log("options:", options);

  const response = (await axios(options)
    .then((res) => {
      if (streamToFile) {
        const fileName = generateFileName(url);
        const filePath = path.join(__dirname, fileName);
        const writer = fs.createWriteStream(filePath);

        return new Promise((resolve, reject) => {
          res.data.pipe(writer);
          writer.on("finish", () => {
            // Close the writer stream when finished writing
            writer.close();
            resolve({
              response: {
                status: res.status,
                statusText: res.statusText,
                headers: res.headers,
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
            data: !dataFromFile ? res.data : undefined,
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
    })) as Outputs;
  return response;
}

// test.
const handler: Handler = async (inputs) => {
  const { method, url, data, headers, params, streamToFile, dataFromFile } =
    inputs;
  const response = await axiosWrapper(
    method,
    url,
    data,
    headers,
    params,
    streamToFile,
    dataFromFile
  );
  console.log("response:", response);
  return response;
};

export { handler };
