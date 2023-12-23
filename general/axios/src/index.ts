import axios, { AxiosError, AxiosRequestConfig } from "axios";
import { Handler } from "./types";
function axiosWrapper(method = "GET", url, data, headers = {}, params = {}) {
  // Set default headers or use provided ones
  const defaultHeaders = {
    ...headers,
  };

  // Configure request options
  const options: AxiosRequestConfig = {
    method,
    url,
    headers: defaultHeaders,
    data,
    params,
  };
  console.log("options:", options);
  // Make the Axios request
  const response = axios(options)
    .then((res) => {
      return {
        response: {
          status: res.status,
          statusText: res.statusText,
          headers: res.headers,
          data: res.data,
          config: res.config,
        },
      };
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
  const { method, url, data, headers, params } = inputs;
  return await axiosWrapper(method, url, data, headers, params);
};

export { handler };
