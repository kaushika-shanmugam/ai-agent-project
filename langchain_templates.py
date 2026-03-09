from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile")
parser = StrOutputParser()

# ── Reusable prompt template with multiple placeholders ───
# {data}      = the actual data to analyse
# {role}      = what kind of expert the AI should be
# {focus}     = what aspect to focus on
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a {role}. Be concise and professional."),
    ("human", """Analyse this data:

{data}

Focus specifically on: {focus}
Give exactly 3 actionable recommendations.""")
])

chain = prompt | llm | parser

# ── Same chain, completely different use cases! ────────────

print("=" * 55)
print("USE CASE 1: Sales Analysis")
print("=" * 55)
result1 = chain.invoke({
    "role": "Oracle database performance specialist",
    "data": """
    Electronics  | Sales: 265,000 | Target: 220,000
    Clothing     | Sales: 117,000 | Target: 150,000
    Sports       | Sales: 32,000  | Target: 60,000
    """,
    "focus": "query optimisation and database bottlenecks"
})
print(result1)

print("\n" + "=" * 55)
print("USE CASE 2: HR Analysis — Same Chain, Different Data!")
print("=" * 55)
result2 = chain.invoke({
    "role": "HR director and workforce analyst",
    "data": """
    DEPARTMENT   | EMPLOYEES | AVG_SALARY | TURNOVER
    Electronics  | 27        | 92,000     | 5%
    Clothing     | 17        | 68,000     | 22%
    Sports       | 6         | 62,000     | 35%
    """,
    "focus": "employee retention and salary competitiveness"
})
print(result2)

print("\n" + "=" * 55)
print("USE CASE 3: Your Jira Data — Same Chain Again!")
print("=" * 55)
result3 = chain.invoke({
    "role": "senior project manager and scrum master",
    "data": """
    PROJ-101 | Story | High   | 5pts | User Login Feature
    PROJ-103 | Bug   | High   | 2pts | Login Page Crashes on Mobile
    PROJ-104 | Story | High   | 8pts | User Registration
    PROJ-107 | Bug   | High   | 1pts | Duplicate Email Registration
    """,
    "focus": "sprint planning and risk mitigation"
})
print(result3)
