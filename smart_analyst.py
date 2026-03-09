from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq()

print("=" * 55)
print("  Smart Oracle Data Analyst")
print("=" * 55)
print("\nPaste your Oracle query result below.")
print("When done, type 'END' on a new line and press Enter:\n")

# ── Let user paste any Oracle data ─────────────────────────
data_lines = []
while True:
    line = input()
    if line.strip() == "END":
        break
    data_lines.append(line)

oracle_data = "\n".join(data_lines)

print("\n✅ Data received! You can now ask questions about it.")
print("Type 'exit' to quit\n")
print("-" * 55)

# ── Start conversation with the pasted data ─────────────────
conversation_history = [
    {
        "role": "system",
        "content": f"""You are a senior Oracle database analyst.
The user has provided the following data from their Oracle database:

{oracle_data}

Answer all questions based on this data clearly and concisely.
Remember the full conversation history and refer back when relevant."""
    }
]

while True:
    user_question = input("\nYou: ")

    if user_question.lower() == "exit":
        print("Goodbye!")
        break

    conversation_history.append({
        "role": "user",
        "content": user_question
    })

    print("\nAnalyst: ", end="", flush=True)

    message = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=conversation_history
    )

    ai_reply = message.choices[0].message.content

    conversation_history.append({
        "role": "assistant",
        "content": ai_reply
    })

    print(ai_reply)
    print("\n" + "-" * 55)
