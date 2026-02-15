const OpenAI = require("openai");

const openai = new OpenAI({ apiKey: process.env.API_KEY });

async function handler(inputs) {
  const { systemMessage, message, model = "gpt-3.5-turbo", apiKey } = inputs;
  const client = apiKey ? new OpenAI({ apiKey }) : openai;

  try {
    const completion = await client.chat.completions.create({
      model,
      messages: [
        {
          role: "system",
          content: systemMessage || "You are a helpful assistant.",
        },
        { role: "user", content: message },
      ],
    });
    console.log("OpenAI response: ", JSON.stringify(completion));
    return {
      response: completion.choices[0].message.content,
    };
  } catch (error) {
    console.error("Error calling OpenAI: ", error);
    return {
      response: "Failed to get response from model",
    };
  }
}

// (async () => {
//   console.log(
//     await handler({
//       systemMessage: "You are a helpful assistant.",
//       messages: [
//         "Generate a linkedin post with smileys that sums up the following listings: \n - Berlin central flat (m) 200$ \n - Paris central flat (m) 300$ \n - London central flat (m) 400$",
//       ],
//     })
//   );
// })();

module.exports = { handler };
