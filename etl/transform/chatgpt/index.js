const OpenAI = require("openai");

const openai = new OpenAI({ apiKey: process.env.API_KEY });

async function handler(inputs) {
  const {
    systemMessage,
    message,
    model = "gpt-3.5-turbo",
    parseResponseToJson = false,
  } = inputs;

  const completion = await openai.chat.completions.create({
    model,
    messages: [
      {
        role: "system",
        content: systemMessage || "You are a helpful assistant.",
      },
      { role: "user", content: message },
    ],
    ...(parseResponseToJson ? { response_format: { type: "json_object" } } : {}),
  });

  const rawContent = completion.choices?.[0]?.message?.content;
  console.log("OpenAI response: ", rawContent);

  if (!rawContent || rawContent.includes("Failed to get response from GPT-3")) {
    throw new Error("Failed to get response");
  }

  if (parseResponseToJson) {
    try {
      const parsed = JSON.parse(rawContent);
      return { response: parsed };
    } catch (err) {
      throw new Error("Failed to parse response as JSON: " + err.message);
    }
  }

  return {
    response: rawContent,
  };
}

module.exports = { handler };
