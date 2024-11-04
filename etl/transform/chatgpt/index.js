const OpenAI = require("openai");

const openai = new OpenAI({ apiKey: process.env.API_KEY });

async function handler(inputs) {
  const { systemMessage, message, model = "gpt-3.5-turbo" } = inputs;

  const completion = await openai.chat.completions.create({
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
  if (!completion.choices || !completion.choices[0] || completion.choices[0].message.content.includes("Failed to get response from GPT-3")) {
    throw new Error("Failed to get response");
  }
  return {
    response: completion.choices[0].message.content,
  };
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
