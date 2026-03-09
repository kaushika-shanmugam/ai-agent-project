from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant")

# ════════════════════════════════════════════════════════
# STEP 1 — LOAD THE PDF
# ════════════════════════════════════════════════════════

print("📄 Loading PDF...")
loader = PyPDFLoader("hr_policy.pdf")
documents = loader.load()
print(f"✅ Loaded {len(documents)} pages")

# ════════════════════════════════════════════════════════
# STEP 2 — SPLIT INTO CHUNKS
# Cut the document into small digestible pieces
# ════════════════════════════════════════════════════════

print("✂️  Splitting into chunks...")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,       # each chunk = max 500 characters
    chunk_overlap=50,     # chunks overlap by 50 chars so nothing is missed
)
chunks = splitter.split_documents(documents)
print(f"✅ Created {len(chunks)} chunks")

# ════════════════════════════════════════════════════════
# STEP 3 — EMBED AND STORE IN VECTOR DATABASE
# Convert chunks to numbers and store in ChromaDB
# ════════════════════════════════════════════════════════

print("🧮 Creating embeddings and storing in vector database...")
embeddings = SentenceTransformerEmbeddings(
    model_name="all-MiniLM-L6-v2"  # free, fast, good quality
)
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"  # saves to disk so we don't rebuild every time
)
print("✅ Vector database ready!")

# ════════════════════════════════════════════════════════
# STEP 4 — CREATE THE SEARCH TOOL
# This tool searches the PDF for relevant chunks
# ════════════════════════════════════════════════════════

@tool
def search_hr_policy(query: str) -> str:
    """Searches the HR policy document for information about 
    salary, leave, performance, remote work or any HR policy topic."""
    
    # Find the 3 most relevant chunks for the query
    results = vectorstore.similarity_search(query, k=3)
    
    if not results:
        return "No relevant information found in the HR policy document."
    
    # Combine the chunks into one response
    combined = "\n\n---\n\n".join([doc.page_content for doc in results])
    return f"Relevant HR Policy information:\n\n{combined}"

# ════════════════════════════════════════════════════════
# STEP 5 — CREATE THE AGENT
# ════════════════════════════════════════════════════════

tools = [search_hr_policy]

system_prompt = """You are a helpful HR Policy assistant for TechCorp International.
You have access to the company HR policy document through your search tool.
ALWAYS search the document before answering any policy question.
Only use information found in the document — never make up policies.
Give clear, friendly answers and mention which policy section your answer comes from."""

agent = create_react_agent(llm, tools, prompt=system_prompt)

# ════════════════════════════════════════════════════════
# STEP 6 — CHAT WITH YOUR PDF!
# ════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  📚 HR Policy AI Assistant")
print("  Ask anything about company HR policies!")
print("  Type 'exit' to quit")
print("=" * 60)
print("\nExample questions:")
print("  - How many days of annual leave do I get?")
print("  - What is the bonus policy?")
print("  - Can I work from home?")
print("  - What happens if I get a low performance rating?")
print("-" * 60)

while True:
    question = input("\nYou: ")

    if question.lower() == "exit":
        print("Goodbye!")
        break

    print("\n🤔 Searching policy document...\n")

    response = agent.invoke({
        "messages": [("human", question)]
    })

    final = response["messages"][-1].content
    print(f"\n✅ HR Assistant: {final}")
    print("\n" + "-" * 60)
