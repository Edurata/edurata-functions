import { describe, expect, it } from "@jest/globals";
import { handler } from "../src";
describe("Deepl", () => {
  it("should make a generic request", async () => {
    const response = await handler({
      sourceTexts: ["Hello World"],
      targetLanguage: "de",
    });
    console.log(response);

    expect(response.translations[0]).toEqual("Hallo Welt");
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
