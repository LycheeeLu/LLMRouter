import os
from dotenv import load_dotenv

load_dotenv()

print("OpenAI key:", os.getenv("OPENAI_API_KEY"))
