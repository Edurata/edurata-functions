import {Handler} from "./types";
import fs from "fs";

const sleep = (ms) => {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

export const handler: Handler = async (inputs) => {
  await sleep(inputs.sleepTimeMs)
  if (inputs.file) {
    const fileData = fs.readFileSync(inputs.file)
    fs.writeFileSync(inputs.file, fileData + " Hey there again!")
  } else {
    fs.writeFileSync(inputs.file, "Hey there!")
  }

  return {
    sleepTimeMs: inputs.sleepTimeMs + 1000,
    file: inputs.file
  }
};