from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
import oracledb
from dotenv import load_dotenv

load_dotenv()

# ════════════════════════════════════════════════════════
# FASTAPI APP
# ════════════════════════════════════════════════════════

app = FastAPI(
    title="HR Intelligence Agent API",
    description="AI Agent that queries Oracle HR database and HR Policy PDF",
    version="1.0.0"
)

# ════════════════════════════════════════════════════════
# REQUEST AND RESPONSE MODELS
# These define what goes IN and comes OUT of your API
# ════════════════════════════════════════════════════════

class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    question: str
    answer: str
    status: str

# ════════════════════════════════════════════════════════
# ORACLE CONNECTION
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
# RAG SETUP — Load PDF once when API starts
# ════════════════════════════════════════════════════════

print("📄 Loading HR Policy document...")
loader = PyPDFLoader("hr_policy.pdf")
documents = loader.load()
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(documents)
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db_api"
)
print("✅ HR Policy document ready!")

# ════════════════════════════════════════════════════════
# TOOLS
# ════════════════════════════════════════════════════════

@tool
def get_all_employees() -> str:
    """Gets all employees with salary, job title and department."""
    sql = """
        SELECT e.FIRST_NAME || ' ' || e.LAST_NAME as NAME,
               e.SALARY, e.JOB_ID, d.DEPARTMENT_NAME
        FROM EMPLOYEES e
        JOIN DEPARTMENTS d ON e.DEPARTMENT_ID = d.DEPARTMENT_ID
        ORDER BY e.SALARY DESC
    """
    return run_query(sql)

@tool
def get_department_summary() -> str:
    """Gets headcount and average salary for each department."""
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
    """Gets the top 10 highest paid employees."""
    sql = """
        SELECT e.FIRST_NAME || ' ' || e.LAST_NAME as NAME,
               e.SALARY, e.JOB_ID, d.DEPARTMENT_NAME
        FROM EMPLOYEES e
        JOIN DEPARTMENTS d ON e.DEPARTMENT_ID = d.DEPARTMENT_ID
        ORDER BY e.SALARY DESC
        FETCH FIRST 10 ROWS ONLY
    """
    return run_query(sql)

@tool
def search_hr_policy(query: str) -> str:
    """Searches the HR Policy PDF for salary, leave, bonus,
    performance, remote work or any HR policy information."""
    results = vectorstore.similarity_search(query, k=3)
    if not results:
        return "No relevant policy information found."
    combined = "\n\n---\n\n".join([doc.page_content for doc in results])
    return f"HR Policy information:\n\n{combined}"

# ════════════════════════════════════════════════════════
# CREATE AGENT
# ════════════════════════════════════════════════════════

tools = [get_all_employees, get_department_summary,
         get_top_earners, search_hr_policy]

system_prompt = """You are a helpful HR Business Intelligence Agent.
You have access to Oracle HR database and HR Policy PDF.
Always use tools to get real data before answering.
Never make up information — only use what tools return.
Give clear, professional answers."""

llm = ChatGroq(model="llama-3.1-8b-instant")
agent = create_react_agent(llm, tools, prompt=system_prompt)

print("✅ Agent ready!")

# ════════════════════════════════════════════════════════
# API ENDPOINTS
# ════════════════════════════════════════════════════════

# ── Health check ──────────────────────────────────────
@app.get("/health")
def health_check():
    """Check if the API is running"""
    return {
        "status": "healthy",
        "message": "HR Intelligence Agent API is running!",
        "version": "1.0.0"
    }

# ── Ask the HR agent anything ─────────────────────────
@app.post("/ask", response_model=AnswerResponse)
def ask_agent(request: QuestionRequest):
    """Ask the HR agent a question about employees or policies"""
    try:
        response = agent.invoke({
            "messages": [("human", request.question)]
        })
        answer = response["messages"][-1].content

        return AnswerResponse(
            question=request.question,
            answer=answer,
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Search HR Policy PDF only ─────────────────────────
@app.post("/search-policy")
def search_policy(request: QuestionRequest):
    """Search the HR Policy PDF directly"""
    try:
        results = vectorstore.similarity_search(request.question, k=3)
        chunks_found = [doc.page_content for doc in results]

        return {
            "question": request.question,
            "results": chunks_found,
            "total_chunks": len(chunks_found),
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── List all departments ───────────────────────────────
@app.get("/departments")
def get_departments():
    """Get all department names from Oracle HR database"""
    try:
        result = run_query("""
            SELECT DEPARTMENT_NAME, 
                   COUNT(e.EMPLOYEE_ID) as HEADCOUNT
            FROM DEPARTMENTS d
            LEFT JOIN EMPLOYEES e 
                ON d.DEPARTMENT_ID = e.DEPARTMENT_ID
            GROUP BY DEPARTMENT_NAME
            ORDER BY DEPARTMENT_NAME
        """)
        return {"departments": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ════════════════════════════════════════════════════════
# RUN THE API
# ════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
