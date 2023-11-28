import { describe, expect, it } from "@jest/globals";
import { handler } from "../src";
describe("Axios handler", () => {
  it("should make a generic request", async () => {
    const response = handler({
      body: JSON.stringify({}),
    });

    expect(response).resolves.toBeTruthy();
  });
});
