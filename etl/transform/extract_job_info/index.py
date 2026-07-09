import openai
import json

def handler(inputs):
    OPENAI_API_KEY = inputs.get("openai_api_key")
    if not OPENAI_API_KEY:
        return {"error": "OPENAI_API_KEY is missing. Ensure it's set in Edurata Secrets."}

    job_description = inputs.get("job_description")
    if not job_description:
        return {"error": "Job description is missing."}

    prompt = f"""
    You are an AI agent designed to extract key details from job descriptions. Based on the following job description, provide the information in JSON format with these fields:
    - "company_name": string
    - "job_name": string
    - "language": string
    - "working_model": string
    - "location": string
    - "role": string
    - "short_job_description": string
    - "salary_expectation": number - without "" (salary expectation in euros per year, if unavailable make a guess based on seniority)

    Job Description:
    {job_description}

    Respond in JSON format only.
    """

    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )

        completion = response.choices[0].message.content.strip()
        
        job_info = json.loads(completion)

        return {"job_info": job_info}
    
    except Exception as e:
        return {"error": f"Error extracting job info: {str(e)}"}