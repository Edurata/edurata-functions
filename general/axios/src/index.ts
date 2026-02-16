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

// Helper function to get nested value from object using dot notation
function getNestedValue(obj: any, path: string): any {
  return path.split(".").reduce((current, key) => current?.[key], obj);
}

// Helper function to set nested value in object using dot notation
function setNestedValue(obj: any, path: string, value: any): void {
  const keys = path.split(".");
  const lastKey = keys.pop();
  const target = keys.reduce((current, key) => {
    if (!current[key]) current[key] = {};
    return current[key];
  }, obj);
  if (lastKey) target[lastKey] = value;
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
  throwError = true,
  pagination = false,
  cursorKey = "",
  cursorAppendMethod = "query",
  cursorParamName = "cursor",
  maxPages = null
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

  // If pagination is disabled, make a single request
  if (!pagination || !cursorKey) {
    console.log("axios options:", {
      method,
      url,
      headers: defaultHeaders,
      params,
      responseType: options.responseType,
      data: dataFromFile ? `[stream from ${dataFromFile}]` : body,
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

  // Pagination logic
  const allPages: any[] = [];
  let pageCount = 0;
  let cursor: any = null;

  // Note: Pagination doesn't work with streamToFile or dataFromFile.
  if (streamToFile || dataFromFile) {
    throw new Error(
      "Pagination is not supported with streamToFile or dataFromFile options"
    );
  }

  do {
    pageCount++;
    if (maxPages && pageCount > maxPages) {
      console.log(`Reached maxPages limit (${maxPages})`);
      break;
    }

    // Reset to original values for each request
    let currentParams = { ...params };
    let currentHeaders = { ...defaultHeaders };
    let currentBody = body
      ? JSON.parse(JSON.stringify(body))
      : {}; // Deep copy to avoid mutation

    // Apply cursor to request based on append method
    if (cursor !== null) {
      if (cursorAppendMethod === "query") {
        currentParams[cursorParamName] = cursor;
      } else if (cursorAppendMethod === "header") {
        currentHeaders[cursorParamName] = String(cursor);
      } else if (cursorAppendMethod === "body") {
        if (typeof currentBody === "object" && currentBody !== null) {
          setNestedValue(currentBody, cursorParamName, cursor);
        } else {
          currentBody = { [cursorParamName]: cursor };
        }
      }
    }

    const paginationOptions: AxiosRequestConfig = {
      method,
      url,
      headers: currentHeaders,
      ...(method !== "GET" && { data: currentBody }),
      params: currentParams,
      responseType: "json",
    };

    console.log(`axios pagination options (page ${pageCount}):`, {
      method,
      url,
      headers: currentHeaders,
      params: currentParams,
      body: currentBody,
      cursor,
    });

    try {
      const res = await axios(paginationOptions);

      // Store this page's response
      allPages.push({
        status: res.status,
        statusText: res.statusText,
        headers: res.headers,
        data: res.data,
      });

      // Extract cursor from response
      cursor = getNestedValue(res.data, cursorKey);
      console.log(`Page ${pageCount} cursor:`, cursor);

      // If no cursor found, stop pagination
      if (cursor === null || cursor === undefined || cursor === "") {
        console.log("No cursor found, stopping pagination");
        break;
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
  } while (cursor !== null && cursor !== undefined && cursor !== "");

  // Return aggregated response
  return {
    response: {
      status: allPages[0]?.status || 200,
      statusText: allPages[0]?.statusText || "OK",
      headers: allPages[0]?.headers || {},
      data: allPages.map((page) => page.data),
      pages: allPages,
      pageCount: allPages.length,
    },
  };
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
    pagination = false,
    cursorKey = "",
    cursorAppendMethod = "query",
    cursorParamName = "cursor",
    maxPages = null,
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
    throwError,
    pagination,
    cursorKey,
    cursorAppendMethod,
    cursorParamName,
    maxPages
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
