from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

client = OpenAI(
    base_url=os.getenv("SARVAM_BASE_URL"),
    api_key=os.getenv("SARVAM_API_KEY"),
).with_options(max_retries=1)

reply = client.chat.completions.create(
    model=os.getenv("SARVAM_MODEL", "sarvam-m"),
    messages=[
        {"role": "system", "content": "You respond in both English and Hindi."},
        {"role": "user", "content": "Say hello, how are you?"},
    ],
    reasoning_effort="medium",
    max_completion_tokens=150,
)

print(reply.choices[0].message.content)
