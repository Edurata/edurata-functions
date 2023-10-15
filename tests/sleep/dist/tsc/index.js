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
    await sleep(inputs.sleepTimeMs);
    if (inputs.file) {
        const fileData = fs_1.default.readFileSync(inputs.file);
        fs_1.default.writeFileSync(inputs.file, fileData + " Hey there again!");
    }
    else {
        fs_1.default.writeFileSync(inputs.file, "Hey there!");
    }
    console.error("Test error inner logs");
    return {
        sleepTimeMs: inputs.sleepTimeMs + 1000,
        file: inputs.file,
    };
};
exports.handler = handler;
