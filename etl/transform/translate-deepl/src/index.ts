import { Handler } from "./types";
import * as deepl from "deepl-node";

const handler: Handler = async (inputs) => {
  const { sourceTexts, targetLanguage } = inputs;
  const apiKey = process.env.DEEPL_API_KEY;
  if (!apiKey) {
    throw new Error("No Deepl API key found");
  }
  const translator = new deepl.Translator(apiKey);
  const result = await translator.translateText(
    sourceTexts,
    null,
    targetLanguage
  );
  return {
    translations: result.map((r) => r.text),
  };
};

export { handler };
