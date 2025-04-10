"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.handler = void 0;
const fs_1 = __importDefault(require("fs"));
const child_process_1 = require("child_process");
const handler = async (inputs) => {
    const { code: codePath } = inputs;
    // Assuming codePath is a directory containing package.json
    try {
        // Synchronously execute npm install in the codePath directory
        console.log("npm installing in ", codePath);
        const tmpNpmDir = "/tmp/npm-tmp";
        fs_1.default.mkdirSync(tmpNpmDir, { recursive: true });
        // install only production dependencies
        (0, child_process_1.execSync)("npm install --only=production --ignore-scripts --no-audit --no-fund --cache /tmp/npm-cache", {
            cwd: codePath,
            stdio: "inherit",
            env: {
                ...process.env,
                // Override all npm-related locations
                npm_config_cache: "/tmp/npm-cache",
                npm_config_tmp: "/tmp/npm-tmp",
                npm_config_prefix: "/tmp/npm-prefix",
                HOME: "/tmp", // for .npmrc fallback
            },
        });
        // remove package.json and package-lock.json since they cause when executing
        if (fs_1.default.existsSync(`${codePath}/package-lock.json`))
            fs_1.default.unlinkSync(`${codePath}/package-lock.json`);
        if (fs_1.default.existsSync(`${codePath}/package.json`))
            fs_1.default.unlinkSync(`${codePath}/package.json`);
        console.log("NPM modules installed successfully.");
    }
    catch (error) {
        console.error("Error installing NPM modules:", error);
        return { code: codePath };
    }
    return { code: codePath };
};
exports.handler = handler;
