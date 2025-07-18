"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.handler = void 0;
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
const sleep = (ms) => {
    return new Promise((resolve) => {
        setTimeout(resolve, ms);
    });
};
const handler = async (inputs) => {
    console.log("Test inner logs");
    const _sleepTime = inputs.sleepTime
        ? typeof inputs.sleepTime === "string"
            ? parseInt(inputs.sleepTime)
            : inputs.sleepTime
        : 1000;
    const _message = inputs.message;
    const _random_file_path = path_1.default.join("/tmp", process.env.DEPLOYMENT_ID + ".txt");
    const _filePath = path_1.default.join("/tmp", inputs.infile || "testFile.txt");
    console.log(_message);
    // print
    await sleep(_sleepTime);
    // Create dummy file
    fs_1.default.writeFileSync(_random_file_path, "Dummy file");
    if (inputs.infile) {
        const inputFilePath = path_1.default.join("/tmp", inputs.infile);
        const fileData = fs_1.default.readFileSync(inputFilePath);
        fs_1.default.writeFileSync(inputFilePath, fileData + _message);
    }
    else {
        fs_1.default.writeFileSync(_filePath, _message);
    }
    console.error("Test error inner logs");
    return {
        message: _message,
        sleepTime: _sleepTime + 1000,
        outfile: _filePath,
        dummyfile: _random_file_path,
    };
};
exports.handler = handler;
