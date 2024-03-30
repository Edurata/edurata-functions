import axios, { AxiosError, AxiosRequestConfig } from "axios";
import { Handler } from "./types";
import * as fs from "fs";
import * as path from "path";

// Helper function to generate a unique file name.
function generateFileName(url: string): string {
  const datePrefix = new Date().toISOString().replace(/[:.]/g, "-");
  const urlHash = Buffer.from(url).toString("hex").substring(0, 6);
  return `download-${datePrefix}-${urlHash}.tmp`;
}

function axiosWrapper(
  method = "GET",
  url,
  data,
  headers = {},
  params = {},
  streamToFile: boolean,
  dataFromFile = ""
) {
  let dataToSend = data;
  const defaultHeaders = {
    ...headers,
  };

  if (dataFromFile) {
    dataToSend = fs.readFileSync(dataFromFile);
  }

  const options: AxiosRequestConfig = {
    method,
    url,
    headers: defaultHeaders,
    data: dataFromFile,
    params,
    responseType: streamToFile ? "stream" : "json",
  };

  console.log("options:", options);

  return axios(options)
    .then((res) => {
      if (streamToFile) {
        const fileName = generateFileName(url);
        const filePath = path.join(__dirname, fileName);
        const writer = fs.createWriteStream(filePath);

        return new Promise((resolve, reject) => {
          res.data.pipe(writer);
          let error: any = null;
          writer.on("error", (err: any) => {
            error = err;
            writer.close();
            reject(err);
          });
          writer.on("close", () => {
            if (!error) {
              resolve({
                response: {
                  status: res.status,
                  statusText: res.statusText,
                  headers: res.headers,
                  file: filePath, // Return the path of the downloaded file
                },
              });
            }
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
    });
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
