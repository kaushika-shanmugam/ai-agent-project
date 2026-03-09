from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

# ── Step 1: Create the AI model ───────────────────────────
# This replaces our old: client = Groq()
llm = ChatGroq(model="llama-3.3-70b-versatile")

print("=" * 50)
print("  LangChain + Groq — First Test")
print("=" * 50)

# ── Step 2: Send a message ────────────────────────────────
# This replaces our old manual messages list
messages = [
    SystemMessage(content="You are a helpful Oracle database expert. Always use database analogies."),
    HumanMessage(content="What is LangChain? Explain it simply.")
]

# ── Step 3: Get response ──────────────────────────────────
# Notice how clean this is compared to before!
response = llm.invoke(messages)

print("\nAI Response:")
print(response.content)

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

print("\n" + "=" * 50)
print("  LangChain Chains Demo")
print("=" * 50)

# ── Step 1: Define a prompt template ─────────────────────
# This is like a reusable SQL template with parameters
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a senior Oracle DBA and business analyst."),
    ("human", "Analyse this data and give 3 key insights:\n\n{data}")
])

# ── Step 2: Define output parser ──────────────────────────
# This cleans up the AI response automatically
parser = StrOutputParser()

# ── Step 3: Create the chain ──────────────────────────────
# The | symbol connects steps together like a pipeline!
# prompt → llm → parser
chain = prompt | llm | parser

# ── Step 4: Run the chain ─────────────────────────────────
sample_data = """
DEPARTMENT   | SALES   | TARGET  | VARIANCE
Electronics  | 265,000 | 220,000 | +45,000
Clothing     | 117,000 | 150,000 | -33,000
Sports       | 32,000  | 60,000  | -28,000
"""

result = chain.invoke({"data": sample_data})

print("\nChain Result:")
print(result)
