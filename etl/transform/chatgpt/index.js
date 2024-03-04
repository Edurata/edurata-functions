const OpenAI = require("openai");

const openai = new OpenAI({ apiKey: process.env.API_KEY });

async function handler(inputs) {
  const { systemMessage, messages } = inputs;

  try {
    const completion = await openai.chat.completions.create({
      model: "gpt-3.5-turbo",
      messages: [
        { role: "system", content: systemMessage },
        messages.map((message) => {
          return { role: "user", content: message };
        }),
      ].flat(),
    });
    console.log("OpenAI response: ", JSON.stringify(completion));
    return {
      response: completion.choices[0].message.content,
    };
  } catch (error) {
    console.error("Error calling OpenAI: ", error);
    return {
      response: "Failed to get response from GPT-3",
    };
  }
}

(async () => {
  console.log(
    await handler({
      systemMessage: "You are a helpful assistant.",
      messages: [
        "Generate a linkedin post with smileys that sums up the following listings: \n - Berlin central flat (m) 200$ \n - Paris central flat (m) 300$ \n - London central flat (m) 400$",
      ],
    })
  );
})();

export { handler };
