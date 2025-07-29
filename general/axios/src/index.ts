import axios, { AxiosError, AxiosRequestConfig } from "axios";
import * as fs from "fs";
import * as path from "path";
const readFile = require("util").promisify(fs.readFile);

// Helper function to generate a unique file name.
function generateFileName(url: string): string {
  const datePrefix = new Date().toISOString().replace(/[:.]/g, "-");
  const urlHash = Buffer.from(url).toString("hex").substring(0, 6);
  return `download-${datePrefix}-${urlHash}`;
}

// Helper function to extract filename from the Content-Disposition header
function getFileNameFromHeader(contentDisposition: string): string | null {
  const match = contentDisposition?.match(/filename="?([^"]+)"?/);
  return match ? match[1] : null;
}

async function axiosWrapper(
  method = "GET",
  url,
  body,
  headers = {},
  params = {},
  streamToFile = false,
  streamToFileName = null,
  dataFromFile = "",
  throwError = true
) {
  let dataToSend = body;
  const defaultHeaders = { ...headers };

  if (dataFromFile) {
    const stats = fs.statSync(dataFromFile);
    dataToSend = fs.createReadStream(dataFromFile);
    defaultHeaders["Content-Length"] = stats.size;
  }

  const options: AxiosRequestConfig = {
    method,
    url,
    headers: defaultHeaders,
    ...(method !== "GET" && { data: dataToSend }),
    params,
    responseType: streamToFile ? "stream" : "json",
  };

  console.log("axios options:", {
    method,
    url,
    headers: defaultHeaders,
    params,
    responseType: options.responseType,
    data: dataFromFile ? `[stream from ${dataFromFile}]` : dataToSend,
  });

  try {
    const res = await axios(options);

    if (streamToFile) {
      const contentDisposition = res.headers["content-disposition"];
      const fileNameFromHeader = contentDisposition
        ? getFileNameFromHeader(contentDisposition)
        : null;
      const fileName =
        streamToFileName || fileNameFromHeader || generateFileName(url);

      const filePath = path.join("/tmp", fileName);
      const writer = fs.createWriteStream(filePath);

      return await new Promise((resolve, reject) => {
        writer.on("error", reject);
        res.data.pipe(writer);
        writer.on("finish", () => {
          writer.close();
          resolve({
            response: {
              status: res.status,
              statusText: res.statusText,
              headers: res.headers,
              file: filePath,
            },
          });
        });
      });
    } else {
      return {
        response: {
          status: res.status,
          statusText: res.statusText,
          headers: res.headers,
          data: !dataFromFile ? res.data : undefined,
        },
      };
    }
  } catch (err) {
    const error = err as AxiosError;
    if (error.response) {
      console.warn("err.response.data:", error.response.data);
      console.warn("err.response.status:", error.response.status);
      console.warn("err.response.headers:", error.response.headers);
    }
    console.error(error.message);
    if (throwError) {
      throw error;
    }
    return null;
  }
}

const handler = async (inputs) => {
  const {
    method = "GET",
    url,
    body,
    headers,
    params,
    streamToFile,
    streamToFileName,
    dataFromFile,
    throwError,
  } = inputs;

  const response = await axiosWrapper(
    method,
    url,
    body,
    headers,
    params,
    streamToFile,
    streamToFileName,
    dataFromFile,
    throwError
  );

  console.log("response:", response);
  return response;
};

module.exports = { handler };

// Sample function call for testing
// const inputs = {
//   method: "GET",
//   url: "https://api.example.com/data",
//   headers: {},
//   params: { query: "value" },
//   streamToFile: true,
//   streamToFileName: null, // Let the system try to extract filename
//   dataFromFile: ""
// };
// handler(inputs).then(response => console.log(response));
