from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile")
parser = StrOutputParser()

# ════════════════════════════════════════════════════════
# MEMORY — LangChain way
# Instead of manually managing a list like Module 1,
# we use MessagesPlaceholder — it slots history in automatically!
# ════════════════════════════════════════════════════════

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a senior Oracle DBA and Business Analyst 
with 20 years experience. You are analysing a Jira project 
for a User Authentication System.

Project context:
- 8 tickets total, 26 story points
- 4 high priority items
- 2 critical bugs (Login crash on mobile, Duplicate email bug)
- Tech areas: frontend, backend, authentication, security

Answer questions based on this context. Remember everything 
discussed in our conversation."""),

    # This is the magic line — slots entire conversation history in!
    MessagesPlaceholder(variable_name="history"),

    ("human", "{question}")
])

chain = prompt | llm | parser

# ── Conversation history — LangChain message objects ──────
# Notice: AIMessage instead of {"role": "assistant"}
# This is the LangChain way of storing history
chat_history = []

print("=" * 55)
print("  🤖 LangChain Agent with Memory")
print("  Your Jira Project Assistant")
print("  Type 'exit' to quit")
print("=" * 55)

while True:
    question = input("\nYou: ")

    if question.lower() == "exit":
        print("Goodbye!")
        break

    # ── Run the chain with history ─────────────────────────
    response = chain.invoke({
        "history": chat_history,    # pass full history
        "question": question        # pass current question
    })

    print(f"\nAssistant: {response}")

    # ── Update history — LangChain way ────────────────────
    # HumanMessage = what you said
    # AIMessage = what the AI replied
    chat_history.append(HumanMessage(content=question))
    chat_history.append(AIMessage(content=response))

    print(f"\n💾 Memory: {len(chat_history)//2} exchanges remembered")
    print("-" * 55)
