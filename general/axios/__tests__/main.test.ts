import { describe, expect, it } from "@jest/globals";
import { handler } from "../src";
describe("Axios handler", () => {
  it("should make a generic request", async () => {
    const response = await handler({
      url: "https://jsonplaceholder.typicode.com/todos/1",
      method: "GET",
    });
    console.log(response);

    expect(response.response!.status).toEqual(200);
  });

  // it("should fail", async () => {
  //   const response = await handler({
  //     url: "https://jsonplaceholder.typicodeee.com/todos/1",
  //     method: "GET",
  //     headers: {},
  //     body: {},
  //   });
  //   console.log(response);

  //   expect(response.error!.code).toEqual("ENOTFOUND");
  // });
});
