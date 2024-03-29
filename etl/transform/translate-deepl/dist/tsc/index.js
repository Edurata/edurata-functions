"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.handler = void 0;
const deepl = __importStar(require("deepl-node"));
const handler = async (inputs) => {
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
        }
        else {
            emptyOrNullIndices.push(i);
        }
    }
    // Translate non-empty/non-null texts
    const translationResult = await translator.translateText(nonEmptyOrNullTexts, null, targetLanguage);
    // Re-insert empty/null elements at the correct positions in the response
    const translations = [];
    let emptyOrNullIndex = 0;
    for (let i = 0; i < sourceTexts.length; i++) {
        if (emptyOrNullIndices.includes(i)) {
            translations.push(sourceTexts[i]); // Insert empty or null element
        }
        else {
            translations.push(translationResult[emptyOrNullIndex].text);
            emptyOrNullIndex++;
        }
    }
    return {
        translations: translations,
    };
};
exports.handler = handler;
