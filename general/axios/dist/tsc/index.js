"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const axios_1 = __importDefault(require("axios"));
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const readFile = require("util").promisify(fs.readFile);
// Helper function to generate a unique file name.
function generateFileName(url) {
    const datePrefix = new Date().toISOString().replace(/[:.]/g, "-");
    const urlHash = Buffer.from(url).toString("hex").substring(0, 6);
    return `download-${datePrefix}-${urlHash}`;
}
// Helper function to extract filename from the Content-Disposition header
function getFileNameFromHeader(contentDisposition) {
    const match = contentDisposition?.match(/filename="?([^"]+)"?/);
    return match ? match[1] : null;
}
async function axiosWrapper(method = "GET", url, data, headers = {}, params = {}, streamToFile = false, streamToFileName = null, dataFromFile = "", throwError = true) {
    let dataToSend = data;
    const defaultHeaders = { ...headers };
    if (dataFromFile) {
        dataToSend = fs.createReadStream(dataFromFile);
    }
    const options = {
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
        data: dataFromFile ? `[stream from ${dataFromFile}]` : data,
    });
    try {
        const res = await (0, axios_1.default)(options);
        if (streamToFile) {
            const contentDisposition = res.headers["content-disposition"];
            const fileNameFromHeader = contentDisposition
                ? getFileNameFromHeader(contentDisposition)
                : null;
            const fileName = streamToFileName || fileNameFromHeader || generateFileName(url);
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
        }
        else {
            return {
                response: {
                    status: res.status,
                    statusText: res.statusText,
                    headers: res.headers,
                    data: !dataFromFile ? res.data : undefined,
                },
            };
        }
    }
    catch (err) {
        const error = err;
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
    const { method = "GET", url, data, headers, params, streamToFile, streamToFileName, dataFromFile, throwError, } = inputs;
    const response = await axiosWrapper(method, url, data, headers, params, streamToFile, streamToFileName, dataFromFile, throwError);
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
