import { fetchData } from "../src/dataFetcher";

describe("fetchData", () => {
  it("fetches data with customizable options", async () => {
    const options = {
      method: "get",
      url: "https://api.example.com/data", // Replace with the actual source URL
      headers: {
        // Customize headers as needed
        Authorization: "Bearer your-api-key",
      },
      // Add any other Axios configuration options as needed
    };

    const response = await fetchData(options);

    // Add your assertions here to validate the response
    expect(response.status).toBe(200);
    expect(response.data).toHaveProperty("data");
  });
});
