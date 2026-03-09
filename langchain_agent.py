from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile")

# ════════════════════════════════════════════════════════
# TOOLS — Notice how simple they are now!
# Just add @tool above any function — LangChain does rest!
# ════════════════════════════════════════════════════════

@tool
def get_all_tickets() -> str:
    """Gets full details of all Jira tickets in the project."""
    return """
    PROJ-101 | Story | High   | 5pts | User Login Feature
             | As a user I want to log in with email and password
             | Comments: Consider OAuth, reuse auth module

    PROJ-102 | Story | Medium | 3pts | Password Reset Flow
             | As a user I want to reset password via email
             | Comments: Expire link after 24hrs, add rate limiting

    PROJ-103 | Bug   | High   | 2pts | Login Page Crashes on Mobile
             | White screen error on iOS Safari on form submit
             | Comments: Reproduced on iPhone 13, form validation issue

    PROJ-104 | Story | High   | 8pts | User Registration
             | As a new user I want to create an account
             | Comments: Email uniqueness, password strength needed

    PROJ-105 | Task  | Medium | 3pts | Email Verification System
             | Implement tokenised email verification after registration
             | Comments: Use existing email service, expire in 48hrs

    PROJ-106 | Task  | Low    | 2pts | Session Timeout Logic
             | Auto session timeout after 30 mins inactivity
             | Comments: Warn user 5 mins before timeout

    PROJ-107 | Bug   | High   | 1pts | Duplicate Email Registration
             | System allows same email registered twice
             | Comments: Critical bug found in UAT, fix before go-live

    PROJ-108 | Story | Low    | 2pts | Remember Me Feature
             | As a user I want to stay logged in for 30 days
             | Comments: Use secure cookie, warn on shared devices
    """

@tool
def get_high_priority_tickets() -> str:
    """Gets only high priority Jira tickets that need urgent attention."""
    return """
    PROJ-101 | Story | High | 5pts | User Login Feature
    PROJ-103 | Bug   | High | 2pts | Login Page Crashes on Mobile
    PROJ-104 | Story | High | 8pts | User Registration
    PROJ-107 | Bug   | High | 1pts | Duplicate Email Registration
    
    Total high priority: 4 tickets | 16 story points
    """

@tool
def get_bugs() -> str:
    """Gets only bug tickets to assess project risks."""
    return """
    PROJ-103 | Bug | High | 2pts | Login Page Crashes on Mobile
             | Status: In Progress
             | Risk: Blocks mobile users from logging in
             | Assignee: Arun Patel

    PROJ-107 | Bug | High | 1pts | Duplicate Email Registration
             | Status: To Do
             | Risk: Critical data integrity issue, found in UAT
             | Assignee: Raj Kumar
             
    Total bugs: 2 | Both High Priority | Must fix before go-live
    """

@tool
def get_project_stats() -> str:
    """Gets overall project statistics and summary."""
    return """
    PROJECT STATISTICS:
    Total Tickets:      8
    Total Story Points: 26
    
    By Type:      Stories: 4 | Bugs: 2 | Tasks: 2
    By Priority:  High: 4   | Medium: 2 | Low: 2
    By Status:    To Do: 7  | In Progress: 1
    
    Tech Areas:   frontend, backend, authentication,
                  email, security, session, mobile
                  
    Key Risk:     2 critical bugs must be resolved before go-live
    Go-Live Risk: HIGH — duplicate email bug is a data integrity issue
    """

# ════════════════════════════════════════════════════════
# CREATE THE AGENT — This is the magic!
# In Module 1 this took 80 lines — now it's 3 lines!
# ════════════════════════════════════════════════════════

# Register all tools
tools = [get_all_tickets, get_high_priority_tickets, get_bugs, get_project_stats]

# Create agent — LangChain handles the entire loop automatically!
agent = create_react_agent(llm, tools)

# ════════════════════════════════════════════════════════
# RUN THE AGENT
# ════════════════════════════════════════════════════════

print("=" * 60)
print("  🤖 LangChain Jira Analysis Agent")
print("=" * 60)

goal = """
You are a senior Business Analyst. Analyse the Jira project 
and produce a professional Requirements Analysis Document with:

1. Executive Summary
2. Functional Requirements  
3. Bug & Risk Analysis
4. Recommended Sprint Plan
5. Open Questions

IMPORTANT: Only use information from the tools.
Call the tools first, then write the document.
Start your final document with: REQUIREMENTS ANALYSIS DOCUMENT
"""

# Run the agent — just one line!
response = agent.invoke({
    "messages": [("human", goal)]
})

# Get the final response
final_response = response["messages"][-1].content
print(final_response)

# Save to file
with open("langchain_requirements.txt", "w") as f:
    f.write(final_response)
print("\n📄 Saved to: langchain_requirements.txt")
