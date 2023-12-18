import { AxiosError, AxiosRequestConfig, AxiosResponse } from "axios";
import { SourceLanguageCode, TargetLanguageCode } from "deepl-node";

export type Inputs = {
  sourceTexts: string[];
  targetLanguage: TargetLanguageCode;
};

export type Outputs = {
  translations: string[];
};

export type Handler = (inputs: Inputs) => Promise<Outputs>;
