"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.handler = void 0;
const child_process_1 = require("child_process");
const handler = async (inputs) => {
    const { code: codePath } = inputs;
    // Assuming codePath is a directory containing package.json
    try {
        // Synchronously execute npm install in the codePath directory
        console.log("npm installing in ", codePath);
        (0, child_process_1.execSync)("npm install", { cwd: codePath, stdio: "inherit" });
        console.log("NPM modules installed successfully.");
    }
    catch (error) {
        console.error("Error installing NPM modules:", error);
        return { error: "Failed to install NPM modules" };
    }
    return { code: codePath };
};
exports.handler = handler;
