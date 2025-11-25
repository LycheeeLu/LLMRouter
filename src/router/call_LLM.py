import os

# LLM API function calls
def call_openai(prompt: str, model: str = "gpt-4o-mini") -> str:
    """Call OpenAI API"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        print("OpenAI key:", os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling OpenAI: {str(e)}"


def call_gemini(prompt: str, model: str = "gemini-1.5-flash") -> str:
    """Call Google Gemini API"""
    try:
        # ignore the warning, the import has been resolved
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model_instance = genai.GenerativeModel(model)
        response = model_instance.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error calling Gemini: {str(e)}"
