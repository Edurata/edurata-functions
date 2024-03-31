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
exports.handler = void 0;
const axios_1 = __importDefault(require("axios"));
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
// Helper function to generate a unique file name.
function generateFileName(url) {
    const datePrefix = new Date().toISOString().replace(/[:.]/g, "-");
    const urlHash = Buffer.from(url).toString("hex").substring(0, 6);
    return `download-${datePrefix}-${urlHash}.tmp`;
}
function axiosWrapper(method = "GET", url, data, headers = {}, params = {}, streamToFile, dataFromFile = "") {
    let dataToSend = data;
    const defaultHeaders = {
        ...headers,
    };
    if (dataFromFile) {
        dataToSend = fs.readFileSync(dataFromFile);
    }
    const options = {
        method,
        url,
        headers: defaultHeaders,
        data: dataToSend,
        params,
        responseType: streamToFile ? "stream" : "json",
    };
    console.log("options:", options);
    return (0, axios_1.default)(options)
        .then((res) => {
        if (streamToFile) {
            const fileName = generateFileName(url);
            const filePath = path.join(__dirname, fileName);
            const writer = fs.createWriteStream(filePath);
            return new Promise((resolve, reject) => {
                res.data.pipe(writer);
                let error = null;
                writer.on("error", (err) => {
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
        }
        else {
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
        .catch((err) => {
        if (err.response) {
            console.warn("err.response.data:", err.response.data);
            console.warn("err.response.status:", err.response.status);
            console.warn("err.response.headers:", err.response.headers);
        }
        console.log(err.message);
        return { error: err };
    });
}
const handler = async (inputs) => {
    const { method, url, data, headers, params, streamToFile, dataFromFile } = inputs;
    return await axiosWrapper(method, url, data, headers, params, streamToFile, dataFromFile);
};
exports.handler = handler;
