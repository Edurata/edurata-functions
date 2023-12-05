import axios, { AxiosError } from "axios";
import { Handler } from "./types";
function axiosWrapper(method, url, data = {}, headers = {}) {
  // Set default headers or use provided ones
  const defaultHeaders = {
    "Content-Type": "application/json",
    ...headers,
  };

  // Configure request options
  const options = {
    method,
    url,
    headers: defaultHeaders,
    data,
  };

  // Make the Axios request
  const response = axios(options)
    .then((res) => {
      return { response: res };
    })
    .catch((err: AxiosError) => {
      if (err.response) {
        console.warn("err.response.data:", err.response.data);
        console.warn("err.response.status:", err.response.status);
        console.warn("err.response.headers:", err.response.headers);
      }
      console.log(err.message);
      return { error: err };
    });
  return response;
}

const handler: Handler = async (inputs) => {
  const { method, url, body, headers } = inputs;
  return await axiosWrapper(method, url, body, headers);
};

export { handler };
