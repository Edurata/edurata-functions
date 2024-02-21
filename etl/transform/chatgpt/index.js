import OpenAI from "openai";

const openai = new OpenAI({ apiKey: process.env.API_KEY });

async function handler(inputs) {
  const { messages } = inputs;

  try {
    const completion = await openai.chat.completions.create({
      model: "gpt-3.5-turbo",
      messages: messages,
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

// Sample function call (commented out)
// (async () => {
//   console.log(
//     await handler({
//       messages: [
//         { role: "system", content: "You are a helpful assistant." },
//         { role: "user", content: "Tell me about the history of AI." },
//       ],
//     })
//   );
// })();

export { handler };
