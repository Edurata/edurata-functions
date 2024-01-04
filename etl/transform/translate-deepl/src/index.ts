import { Handler } from "./types";
import * as deepl from "deepl-node";

const handler: Handler = async (inputs) => {
  const { sourceTexts, targetLanguage } = inputs;
  const apiKey = process.env.DEEPL_API_KEY;
  if (!apiKey) {
    throw new Error("No Deepl API key found");
  }
  const translator = new deepl.Translator(apiKey);

  // Filter out empty elements from sourceTexts and keep track of their positions
  const nonEmptyTexts = [];
  const emptyIndices = [];
  for (let i = 0; i < sourceTexts.length; i++) {
    if (sourceTexts[i].trim() !== "") {
      nonEmptyTexts.push(sourceTexts[i]);
    } else {
      emptyIndices.push(i);
    }
  }

  // Translate non-empty texts
  const translationResult = await translator.translateText(
    nonEmptyTexts,
    null,
    targetLanguage
  );

  // Re-insert empty elements at the correct positions in the response
  const translations = [];
  let emptyIndex = 0;

  for (let i = 0; i < sourceTexts.length; i++) {
    if (emptyIndices.includes(i)) {
      translations.push(""); // Insert empty string
    } else {
      translations.push(translationResult[emptyIndex].text);
      emptyIndex++;
    }
  }

  return {
    translations: translations,
  };
};

export { handler };
