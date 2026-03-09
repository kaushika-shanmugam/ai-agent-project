from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq()

# ── Simulated Oracle Query Result ──────────────────────────
oracle_data = """
DEPARTMENT   | SALES_AMOUNT | TARGET  | EMPLOYEES | REGION
-------------|--------------|---------|-----------|-------
Electronics  | 125,000      | 100,000 | 12        | North
Clothing     | 45,000       | 80,000  | 8         | North
Furniture    | 98,000       | 90,000  | 10        | South
Sports       | 32,000       | 60,000  | 6         | South
Electronics  | 140,000      | 120,000 | 15        | East
Clothing     | 72,000       | 70,000  | 9         | East
"""

print("=" * 50)
print("  Oracle Sales Data AI Analyst")
print("  Type your question, press Enter")
print("  Type 'exit' to quit")
print("=" * 50)

# ── This loop lets you ask multiple questions ───────────────
while True:

    # Ask the user to type a question
    user_question = input("\nYour question: ")

    # Exit if user types 'exit'
    if user_question.lower() == "exit":
        print("Goodbye!")
        break

    # Build the prompt
    prompt = f"""
Here is data from our Oracle sales database for Q4 2024:
{oracle_data}

Based on this data, please answer the following:
{user_question}

Give a clear, concise business analysis.
"""

    print("\nAnalysing... \n")

    # Send to AI
    message = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a senior business analyst with deep experience in sales data. Give clear, actionable insights."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    print(message.choices[0].message.content)
    print("\n" + "-" * 50)
