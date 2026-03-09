import oracledb
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile")

# ════════════════════════════════════════════════════════
# ORACLE CONNECTION
# ════════════════════════════════════════════════════════

def get_oracle_connection():
    # This line enables thick mode for older Oracle versions
    oracledb.init_oracle_client(
        lib_dir=r"C:\oraclexe\app\oracle\instantclient_21_20"
    )
    connection = oracledb.connect(
        user="HR",
        password="hr",
        dsn="localhost:1521/xe"
    )
    return connection

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
# TOOLS
# ════════════════════════════════════════════════════════

@tool
def get_all_employees() -> str:
    """Gets all employees with their salary, job title and department."""
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
    """Gets summary of each department with headcount and average salary."""
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
    """Gets the top 10 highest paid employees in the company."""
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
def get_salary_by_job() -> str:
    """Gets average salary grouped by job title."""
    sql = """
        SELECT JOB_ID,
               COUNT(*) as EMPLOYEE_COUNT,
               ROUND(AVG(SALARY), 0) as AVG_SALARY,
               MIN(SALARY) as MIN_SALARY,
               MAX(SALARY) as MAX_SALARY
        FROM EMPLOYEES
        GROUP BY JOB_ID
        ORDER BY AVG_SALARY DESC
    """
    return run_query(sql)

@tool
def get_employees_no_manager() -> str:
    """Gets employees who have no manager assigned."""
    sql = """
        SELECT FIRST_NAME || ' ' || LAST_NAME as NAME,
               JOB_ID,
               SALARY,
               DEPARTMENT_ID
        FROM EMPLOYEES
        WHERE MANAGER_ID IS NULL
    """
    return run_query(sql)

# ════════════════════════════════════════════════════════
# CREATE THE AGENT
# ════════════════════════════════════════════════════════

tools = [
    get_all_employees,
    get_department_summary,
    get_top_earners,
    get_salary_by_job,
    get_employees_no_manager
]

system_prompt = """You are a helpful Oracle HR database analyst.
You have access to tools that query a real Oracle HR database.
ALWAYS call the appropriate tool first before answering.
Never guess or make up data — only use what the tools return.
Give clear, friendly and professional answers."""

agent = create_react_agent(
    llm,
    tools,
    prompt=system_prompt
)

# ════════════════════════════════════════════════════════
# RUN
# ════════════════════════════════════════════════════════

print("=" * 60)
print("  🤖 Oracle HR Database AI Agent")
print("  Ask anything about your HR data!")
print("  Type 'exit' to quit")
print("=" * 60)
print("\nExample questions:")
print("  - Who are the highest paid employees?")
print("  - Which department has the most employees?")
print("  - What is the average salary by job title?")
print("-" * 60)

while True:
    question = input("\nYou: ")

    if question.lower() == "exit":
        print("Goodbye!")
        break

    print("\n🤔 Agent thinking...\n")

    response = agent.invoke({
        "messages": [("human", question)]
    })

    final = response["messages"][-1].content
    print(f"\n✅ Agent: {final}")
    print("\n" + "-" * 60)
