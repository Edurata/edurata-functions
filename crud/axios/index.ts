import axios, { AxiosRequestConfig, AxiosResponse } from "axios";

/**
 * Generic function to fetch data using Axios with customizable options.
 * @param options - Axios request configuration options.
 * @returns Promise<AxiosResponse<T>> - A promise that resolves with the response data.
 */
export async function handler<T>(
  options: AxiosRequestConfig
): Promise<AxiosResponse<T>> {
  try {
    const response = await axios(options);
    return response;
  } catch (error) {
    console.error("Error fetching data:", error);
    throw error;
  }
}
