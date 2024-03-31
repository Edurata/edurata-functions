import fs from "fs";
import { execSync } from "child_process";

const handler = async (inputs) => {
  const { code: codePath } = inputs;

  // Assuming codePath is a directory containing package.json
  try {
    // Synchronously execute npm install in the codePath directory
    console.log("npm installing in ", codePath);
    // install only production dependencies
    execSync("npm install --only=production", {
      cwd: codePath,
      stdio: "inherit",
    });
    console.log("NPM modules installed successfully.");
  } catch (error) {
    console.error("Error installing NPM modules:", error);
    return { code: codePath };
  }

  return { code: codePath };
};

export { handler };
