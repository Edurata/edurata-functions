import { describe, expect, it } from "@jest/globals";
import { handler } from "../src";
describe("Axios handler", () => {
  it("should make a generic request", async () => {
    const response = handler({
        url: "https://jsonplaceholder.typicode.com/todos/1",
        method: "GET",
        headers: {},
        body: JSON.stringify({}),
    });

    expect(response).resolves.toBeTruthy();
  });
});
