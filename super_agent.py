import oracledb
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant")

# ════════════════════════════════════════════════════════
# PART 1 — ORACLE CONNECTION
# ════════════════════════════════════════════════════════

def get_oracle_connection():
    oracledb.init_oracle_client(
        lib_dir=r"C:\oraclexe\app\oracle\instantclient_21_20"
    )
    return oracledb.connect(
        user="HR",
        password="hr",
        dsn="localhost:1521/xe"
    )

def run_query(sql):
    try:
        conn = get_oracle_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        result = " | ".join(columns) + "\n"
        result += "-" * 60 + "\n"
        for row in rows:
            result += " | ".join(str(val) for val in row) + "\n"
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        return f"Query error: {str(e)}"

# ════════════════════════════════════════════════════════
# PART 2 — RAG SETUP (PDF Knowledge)
# ════════════════════════════════════════════════════════

print("📄 Loading HR Policy document...")
loader = PyPDFLoader("hr_policy.pdf")
documents = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
chunks = splitter.split_documents(documents)

embeddings = SentenceTransformerEmbeddings(
    model_name="all-MiniLM-L6-v2"
)
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db_super"
)
print("✅ HR Policy document ready!")

# ════════════════════════════════════════════════════════
# PART 3 — ALL TOOLS COMBINED
# Oracle tools + PDF search tool = Super Agent!
# ════════════════════════════════════════════════════════

@tool
def get_all_employees() -> str:
    """Gets all employees with name, salary, job title and department 
    from the Oracle HR database."""
    sql = """
        SELECT e.FIRST_NAME || ' ' || e.LAST_NAME as NAME,
               e.SALARY,
               e.JOB_ID,
               d.DEPARTMENT_NAME
        FROM EMPLOYEES e
        JOIN DEPARTMENTS d ON e.DEPARTMENT_ID = d.DEPARTMENT_ID
        ORDER BY e.SALARY DESC
    """
    return run_query(sql)

@tool
def get_department_summary() -> str:
    """Gets headcount and average salary for each department 
    from the Oracle HR database."""
    sql = """
        SELECT d.DEPARTMENT_NAME,
               COUNT(e.EMPLOYEE_ID) as HEADCOUNT,
               ROUND(AVG(e.SALARY), 0) as AVG_SALARY,
               MIN(e.SALARY) as MIN_SALARY,
               MAX(e.SALARY) as MAX_SALARY
        FROM DEPARTMENTS d
        LEFT JOIN EMPLOYEES e ON d.DEPARTMENT_ID = e.DEPARTMENT_ID
        GROUP BY d.DEPARTMENT_NAME
        HAVING COUNT(e.EMPLOYEE_ID) > 0
        ORDER BY AVG_SALARY DESC
    """
    return run_query(sql)

@tool
def get_top_earners() -> str:
    """Gets the top 10 highest paid employees from Oracle HR database."""
    sql = """
        SELECT e.FIRST_NAME || ' ' || e.LAST_NAME as NAME,
               e.SALARY,
               e.JOB_ID,
               d.DEPARTMENT_NAME
        FROM EMPLOYEES e
        JOIN DEPARTMENTS d ON e.DEPARTMENT_ID = d.DEPARTMENT_ID
        ORDER BY e.SALARY DESC
        FETCH FIRST 10 ROWS ONLY
    """
    return run_query(sql)

@tool
def search_hr_policy(query: str) -> str:
    """Searches the HR Policy PDF document for information about
    salary bands, leave policy, bonus, performance, remote work
    or any other HR policy topic."""
    results = vectorstore.similarity_search(query, k=3)
    if not results:
        return "No relevant policy information found."
    combined = "\n\n---\n\n".join([doc.page_content for doc in results])
    return f"HR Policy information:\n\n{combined}"

# ════════════════════════════════════════════════════════
# PART 4 — THE SUPER AGENT
# ════════════════════════════════════════════════════════

tools = [
    get_all_employees,
    get_department_summary,
    get_top_earners,
    search_hr_policy,      # ← PDF search tool combined!
]

system_prompt = """You are an intelligent HR Business Intelligence Agent 
for TechCorp International.

You have TWO sources of information:
1. Oracle HR Database — real employee data, salaries, departments
2. HR Policy PDF — company policies on salary bands, leave, bonus etc.

Use BOTH sources to give complete, accurate answers.
When answering questions about specific employees — use Oracle tools.
When answering questions about policies — use search_hr_policy tool.
For complex questions — use BOTH sources and combine the insights.

Always be clear, professional and mention where your information came from.
Never make up data — only use what the tools return."""

agent = create_react_agent(llm, tools, prompt=system_prompt)

# ════════════════════════════════════════════════════════
# PART 5 — INTERACTIVE CHAT WITH MEMORY
# ════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  🤖 Super HR Intelligence Agent")
print("  Oracle DB + HR Policy PDF combined!")
print("  Type 'exit' to quit")
print("=" * 60)
print("\nTry these powerful combined questions:")
print("  - Which employees earn above Band C salary?")
print("  - What is the bonus policy and who are our top earners?")
print("  - How many leave days do senior employees get?")
print("  - Give me a full HR report on our IT department")
print("-" * 60)

# Conversation memory
chat_history = []

while True:
    question = input("\nYou: ")

    if question.lower() == "exit":
        print("Goodbye!")
        break

    print("\n🤔 Agent thinking...\n")

    # Build messages with memory
    messages = []
    for human, ai in zip(chat_history[::2], chat_history[1::2]):
        messages.append(human)
        messages.append(ai)
    messages.append(("human", question))

    response = agent.invoke({
        "messages": messages
    })

    final = response["messages"][-1].content

    # Update memory
    chat_history.append(("human", question))
    chat_history.append(("assistant", final))

    print(f"\n✅ Agent: {final}")
    print(f"\n💾 Memory: {len(chat_history)//2} exchanges")
    print("\n" + "-" * 60)
