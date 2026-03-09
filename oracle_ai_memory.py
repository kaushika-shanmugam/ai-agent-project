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

# ── Conversation History List ───────────────────────────────
# This is the KEY difference from Class 2
# We start with just the system message
# Then we KEEP ADDING to this list as conversation grows
conversation_history = [
    {
        "role": "system",
        "content": f"""You are a senior Oracle database analyst and business intelligence expert.
You have been given the following sales data from an Oracle database:

{oracle_data}

Answer all questions based on this data. Remember previous questions
in our conversation and refer back to them when relevant.
Be concise, friendly and use business language."""
    }
]

print("=" * 50)
print("  Oracle AI Analyst — With Memory!")
print("  I remember everything you ask me.")
print("  Type 'exit' to quit")
print("=" * 50)

while True:

    # Get user question
    user_question = input("\nYou: ")

    if user_question.lower() == "exit":
        print("Goodbye!")
        break

    # ── Step 1: Add user question to history ───────────────
    conversation_history.append({
        "role": "user",
        "content": user_question
    })

    print("\nAnalyst: ", end="", flush=True)

    # ── Step 2: Send ENTIRE history to AI ──────────────────
    # This is the key — we send the whole conversation, not just the latest question
    message = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=conversation_history
    )

    # ── Step 3: Get AI reply ────────────────────────────────
    ai_reply = message.choices[0].message.content

    # ── Step 4: Add AI reply to history ────────────────────
    # Now the AI's answer becomes part of the conversation too
    conversation_history.append({
        "role": "assistant",
        "content": ai_reply
    })

    print(ai_reply)
    print("\n" + "-" * 50)
