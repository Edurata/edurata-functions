import { AxiosError, AxiosRequestConfig, AxiosResponse } from "axios";

export type Inputs = AxiosRequestConfig;

export type Outputs = {
  response?: AxiosResponse<any, any>;
  error?: AxiosError<any>;
};

export type Handler = (inputs: Inputs) => Promise<Outputs>;
