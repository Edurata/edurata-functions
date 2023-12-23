"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.handler = void 0;
const axios_1 = __importDefault(require("axios"));
function axiosWrapper(method = "GET", url, data, headers = {}, params = {}) {
    // Set default headers or use provided ones
    const defaultHeaders = {
        ...headers,
    };
    // Configure request options
    const options = {
        method,
        url,
        headers: defaultHeaders,
        data,
        params,
    };
    console.log("options:", options);
    // Make the Axios request
    const response = (0, axios_1.default)(options)
        .then((res) => {
        return {
            response: {
                status: res.status,
                statusText: res.statusText,
                headers: res.headers,
                data: res.data,
                config: res.config,
            },
        };
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
    return response;
}
const handler = async (inputs) => {
    const { method, url, data, headers, params } = inputs;
    return await axiosWrapper(method, url, data, headers, params);
};
exports.handler = handler;
