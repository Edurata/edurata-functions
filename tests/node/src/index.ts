import { Handler } from "./types";
import fs from "fs";
import path from "path";

const sleep = (ms) => {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
};

export const handler: Handler = async (inputs) => {
  console.log("Test inner logs");
  const _sleepTime = inputs.sleepTime
    ? typeof inputs.sleepTime === "string"
      ? parseInt(inputs.sleepTime)
      : inputs.sleepTime
    : 1000;
  const _message = inputs.message;
  const _random_file_path = path.join("/tmp", process.env.DEPLOYMENT_ID + ".txt");
  const _filePath = path.join("/tmp", inputs.infile || "testFile.txt");

  console.log(_message);

  // print
  await sleep(_sleepTime);

  // Create dummy file
  fs.writeFileSync(_random_file_path, "Dummy file");

  if (inputs.infile) {
    const inputFilePath = path.join("/tmp", inputs.infile);
    const fileData = fs.readFileSync(inputFilePath);
    fs.writeFileSync(inputFilePath, fileData + _message);
  } else {
    fs.writeFileSync(_filePath, _message);
  }
  console.error("Test error inner logs");
  return {
    message: _message,
    sleepTime: _sleepTime + 1000,
    outfile: _filePath,
    dummyfile: _random_file_path,
  };
};
