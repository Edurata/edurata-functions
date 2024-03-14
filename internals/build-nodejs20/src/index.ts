import fs from "fs";
import { execSync } from "child_process";

const handler = async (inputs) => {
  const { code: codePath } = inputs;

  const code = fs.readFileSync(codePath, "utf8");

  // Assuming codePath is a directory containing package.json
  try {
    // Synchronously execute npm install in the codePath directory
    execSync("npm install", { cwd: codePath, stdio: "inherit" });
    console.log("NPM modules installed successfully.");
  } catch (error) {
    console.error("Error installing NPM modules:", error);
    return { error: "Failed to install NPM modules" };
  }

  return { code: codePath };
};

export { handler };
