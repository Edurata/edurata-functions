import { describe, expect, it } from "@jest/globals";
import { handler } from "../src";
describe("Axios handler", () => {
  // it("should make a generic request", async () => {
  //   const response = await handler({
  //     url: "https://jsonplaceholder.typicode.com/todos/1",
  //     method: "GET",
  //   });
  //   console.log(response);

  //   expect(response.response!.status).toEqual(200);
  // });
  it("should make an upload", async () => {
    // const response = await handler({
    //   url: "https://jsonplaceholder.typicode.com/posts/1",
    //   method: "PUT",
    //   data: "Hello, world!",
    // });

    const response = await handler({
      method: "PUT",
      dataFromFile: "__tests__/test.zip",
      url: "https://edurata-customer-functions-dev.s3.eu-central-1.amazonaws.com/9b68adb4-9166-4882-b4dc-a02c9cce5911/mysql_query_function/5.zip?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAUMVOOLNFWM64GUY6%2F20240423%2Feu-central-1%2Fs3%2Faws4_request&X-Amz-Date=20240423T153530Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEDAaDGV1LWNlbnRyYWwtMSJHMEUCIG4DMThsqkn93AbveDR6arjMGm0wO4i7MV%2FW3fiMyXLDAiEAyJCnPhbcdcztc1tobsGWxJz8tfzTUM4ItpcZQiWkiqkqsQIIeRAAGgwzMDIwODcyOTc4NjciDBM%2BV9rsQrsuuHW3xCqOAhfZhMDHXLVMXyfV4XtTcJHAjhR7POmb39ETww8%2F3Iincgl120rQ6%2BEbyxlUNuHfkUe1E%2FpKS5ytdBiyhfccSgcnMjxBf%2BVOg1%2FopG9WJse%2FWxv5YjbKNJCa7gYxOQqKSjyUQhd6QT2kmU2s9L36rU%2FC%2F7cdvSnHE1HHgyTQ08AXjBi9ZGs8iwrFAxWYWy90d6jt3ElGiN0wx8AvC0fCvJMGg4o3Scsxjuxcdcs90YT3GqZHr8tInwKgefdRQuco5Xd8fqZaLJ0EdMvGAYXysq9SOjrou0FlCQvbgAx8NOTvVcmtce%2BFBNrJ7AUUgePfCx4yBqPK1MBgFRoFqXarI2ORdX3cT3dG2OjgrMZD%2BjDCqp%2BxBjqdATT8Nt7EilaAKbsKpcrV7NFa72EH30FiadU4i2vMKKTnfG7wDm4omEtF49UE%2FowuejD6FrNBS4kS1tmVQhuMBR720q%2Fldlnh12Tv%2BIYkM%2BYR7LM92W%2Bfn10Gw%2BgC8ej2ATCF5j1pZMiesdbOB8y%2BdmQp5CBhwLAYKIX9TkqbN8NcZQN4eE4lAGStiZjAp3PfQ0VBnJ8AWO3N6QMkyD0%3D&X-Amz-Signature=76b11216f8c13b3a186638f7ae65bbcdeadc04a726322c951c352aefdd273a38&X-Amz-SignedHeaders=host&x-id=PutObject",
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
