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
  return axios(options)
    .then((response) => response.data)
    .catch((error) => {
      // Handle or log error
      console.error("Axios request failed:", error);
      throw error;
    });
}

const handler: Handler = async (inputs) => {
  const { method, url, body, headers } = inputs;
  const response = await axiosWrapper(method, url, body, headers);
  return {
    response: response.data,
  };
};

export { handler };
