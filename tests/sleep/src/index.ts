import { Handler } from "./types";
import fs from "fs";

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
  const _filePath = inputs.file || "testFile.txt";
  await sleep(_sleepTime);
  if (inputs.file) {
    const fileData = fs.readFileSync(inputs.file);
    fs.writeFileSync(inputs.file, fileData + " Hey there again!");
  } else {
    fs.writeFileSync(_filePath, "Hey there!");
  }
  console.error("Test error inner logs");
  return {
    sleepTime: _sleepTime + 1000,
    file: _filePath,
    sleepTimeObject: {
      sleepTimeArray: [_sleepTime],
    },
  };
};
