import axios from "axios";
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
      return res;
    })
    .catch((err) => {
      let message =
        typeof err.response !== "undefined"
          ? err.response.data.message
          : err.message;
      console.warn("message:", message);
      console.warn("headers:", err.response.headers);
    });
  return response;
}

const handler: Handler = async (inputs) => {
  const { method, url, body, headers } = inputs;
  const response = await axiosWrapper(method, url, body, headers);
  if (response) {
    return {
      response,
    };
  }
  return {
    response: response ? response.data : null,
  };
};

export { handler };
