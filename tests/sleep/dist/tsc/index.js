"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.handler = void 0;
const fs_1 = __importDefault(require("fs"));
const sleep = (ms) => {
    return new Promise((resolve) => {
        setTimeout(resolve, ms);
    });
};
const handler = async (inputs) => {
    console.log("Test inner logs");
    const _sleepTime = inputs.sleepTime || 1000;
    const _filePath = inputs.file || "testFile.txt";
    await sleep(_sleepTime);
    if (inputs.file) {
        const fileData = fs_1.default.readFileSync(inputs.file);
        fs_1.default.writeFileSync(inputs.file, fileData + " Hey there again!");
    }
    else {
        fs_1.default.writeFileSync(_filePath, "Hey there!");
    }
    console.error("Test error inner logs");
    return {
        sleepTime: _sleepTime + 1000,
        file: _filePath,
    };
};
exports.handler = handler;
