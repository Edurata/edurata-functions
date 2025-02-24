import openai

def handler(inputs):
    # Fetch API key
    api_key = inputs.get("openai_api_key")
    if not api_key:
        return {"error": "OPENAI_API_KEY is missing. Ensure it's set in Edurata Secrets."}

    # Fetch required inputs
    raw_content = inputs.get("raw_content")
    record_id = inputs.get("record_id")
    messages = inputs.get("messages")  # Dynamic message prompt
    model = inputs.get("model", "gpt-4")  # Default to GPT-4
    temperature = inputs.get("temperature", 0.7)  # Default temperature

    if not raw_content:
        return {"error": "raw_content is missing."}
    if not record_id:
        return {"error": "record_id is missing."}
    if not messages:
        return {"error": "messages array is missing."}

    try:
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=api_key)

        # Call OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )

        return {
            "id": record_id,  # Return ID for mapping
            "generated_content": response.choices[0].message.content
        }

    except openai.OpenAIError as e:
        return {"error": f"OpenAI API error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
