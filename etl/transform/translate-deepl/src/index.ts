import { Handler } from "./types";
import * as deepl from "deepl-node";

const handler: Handler = async (inputs) => {
  const { sourceTexts, targetLanguage } = inputs;
  const apiKey = process.env.DEEPL_API_KEY;
  if (!apiKey) {
    throw new Error("No Deepl API key found");
  }
  const translator = new deepl.Translator(apiKey);

  // Filter out empty and null elements from sourceTexts and keep track of their positions
  const nonEmptyOrNullTexts = [];
  const emptyOrNullIndices = [];
  for (let i = 0; i < sourceTexts.length; i++) {
    if (sourceTexts[i] !== null && sourceTexts[i].trim() !== "") {
      nonEmptyOrNullTexts.push(sourceTexts[i]);
    } else {
      emptyOrNullIndices.push(i);
    }
  }

  // Translate non-empty/non-null texts
  const translationResult = await translator.translateText(
    nonEmptyOrNullTexts,
    null,
    targetLanguage
  );

  // Re-insert empty/null elements at the correct positions in the response
  const translations = [];
  let emptyOrNullIndex = 0;

  for (let i = 0; i < sourceTexts.length; i++) {
    if (emptyOrNullIndices.includes(i)) {
      translations.push(sourceTexts[i]); // Insert empty or null element
    } else {
      translations.push(translationResult[emptyOrNullIndex].text);
      emptyOrNullIndex++;
    }
  }

  return {
    translations: translations,
  };
};

export { handler };
