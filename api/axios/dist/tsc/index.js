"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.handler = void 0;
const axios_1 = __importDefault(require("axios"));
function axiosWrapper(method, url, data = {}, headers = {}) {
    // Set default headers or use provided ones
    const defaultHeaders = {
        "Content-Type": "application/json",
        ...headers,
    };
    // Configure request options
    const options = {
        method,
        url,
        headers: defaultHeaders,
        data,
    };
    // Make the Axios request
    return (0, axios_1.default)(options)
        .then((response) => response.data)
        .catch((error) => {
        // Handle or log error
        console.error("Axios request failed:", error);
        throw error;
    });
}
const handler = async (inputs) => {
    const { method, url, body, headers } = inputs;
    const response = await axiosWrapper(method, url, body, headers);
    return {
        response: response.data,
    };
};
exports.handler = handler;
