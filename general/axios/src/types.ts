import { AxiosError, AxiosRequestConfig, AxiosResponse } from "axios";

export type Inputs = AxiosRequestConfig & {
  streamToFile: boolean;
  dataFromFile: string;
};

export type Outputs = {
  response?: AxiosResponse<any, any>;
  error?: AxiosError<any>;
};

export type Handler = (inputs: Inputs) => Promise<Outputs>;
