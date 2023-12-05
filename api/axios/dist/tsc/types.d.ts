import { AxiosError, AxiosResponse } from "axios";
export type Inputs = {
    url: string;
    method: string;
    headers: object;
    body: object;
};
export type Outputs = {
    response?: AxiosResponse<any, any>;
    error?: AxiosError<any>;
};
export type Handler = (inputs: Inputs) => Promise<Outputs>;
