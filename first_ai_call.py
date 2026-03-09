from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq()

message = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "system",
            "content": "You are an expert Oracle DBA with 20 years experience. Always explain things using Oracle and database examples. Be concise and friendly."
        },
        {
            "role": "user",
            "content": "What is machine learning? Explain it to me like I am an Oracle developer.?"
        }
    ]
)

print(message.choices[0].message.content)
