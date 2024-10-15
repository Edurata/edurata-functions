import axios, { AxiosError, AxiosRequestConfig } from "axios";
import * as fs from "fs";
import * as path from "path";
const readFile = require("util").promisify(fs.readFile);

// Helper function to extract filename from Content-Disposition or URL
function getFileNameFromHeadersOrUrl(res, url: string): string {
  const disposition = res.headers["content-disposition"];
  let fileName = "";

  if (disposition && disposition.includes("filename=")) {
    const fileNameMatch = disposition.match(/filename="?(.+)"?/);
    if (fileNameMatch?.[1]) {
      fileName = fileNameMatch[1];
    }
  }

  // Fallback to extracting from the URL
  if (!fileName) {
    const urlPath = new URL(url).pathname;
    fileName = path.basename(urlPath);
  }

  return fileName || generateFileName(url); // Fallback to unique name if necessary
}

// Helper function to generate a unique file name.
function generateFileName(url: string): string {
  const datePrefix = new Date().toISOString().replace(/[:.]/g, "-");
  const urlHash = Buffer.from(url).toString("hex").substring(0, 6);
  return `download-${datePrefix}-${urlHash}`;
}

async function axiosWrapper(
  method = "GET",
  url,
  data,
  headers = {},
  params = {},
  streamToFile = false,
  streamToFileName = null,
  dataFromFile = ""
) {
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

  const response = await axios(options)
    .then((res) => {
      if (streamToFile) {
        const fileName =
          streamToFileName || getFileNameFromHeadersOrUrl(res, url);
        const filePath = path.join(__dirname, fileName);
        const writer = fs.createWriteStream(filePath);

        return new Promise((resolve, reject) => {
          res.data.pipe(writer);
          writer.on("finish", () => {
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

  return response;
}

// Sample function call for testing
// const inputs = {
//   method: "GET",
//   url: "https://example.com/file.txt",
//   headers: {},
//   params: {},
//   streamToFile: true,
//   dataFromFile: ""
// };
// handler(inputs).then(response => console.log(response));
