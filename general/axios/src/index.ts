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
        // Check if Content-Disposition header is available to extract filename
        const contentDisposition = res.headers["content-disposition"];
        const fileNameFromHeader = contentDisposition
          ? getFileNameFromHeader(contentDisposition)
          : null;
        const fileName =
          streamToFileName || fileNameFromHeader || generateFileName(url);

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

// test.
const handler = async (inputs) => {
  const {
    method,
    url,
    data,
    headers,
    params,
    streamToFile,
    streamToFileName,
    dataFromFile,
  } = inputs;
  const response = await axiosWrapper(
    method,
    url,
    data,
    headers,
    params,
    streamToFile,
    streamToFileName,
    dataFromFile
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
