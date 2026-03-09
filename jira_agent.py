from groq import Groq
from dotenv import load_dotenv
import json

load_dotenv()
client = Groq()

# ════════════════════════════════════════════════════════
# JIRA DATA — Simulated tickets
# (Replace this section with real Jira API call later)
# ════════════════════════════════════════════════════════

jira_tickets = [
    {
        "id": "PROJ-101",
        "type": "Story",
        "title": "User Login Feature",
        "description": "As a user I want to log in using my email and password so that I can access my account securely",
        "priority": "High",
        "status": "To Do",
        "story_points": 5,
        "assignee": "Raj Kumar",
        "labels": ["frontend", "authentication"],
        "comments": [
            "Need to consider OAuth support for future",
            "Check if existing auth module can be reused"
        ]
    },
    {
        "id": "PROJ-102",
        "type": "Story",
        "title": "Password Reset Flow",
        "description": "As a user I want to reset my password via email so that I can regain access if I forget it",
        "priority": "Medium",
        "status": "To Do",
        "story_points": 3,
        "assignee": "Priya Sharma",
        "labels": ["frontend", "authentication", "email"],
        "comments": [
            "Should expire reset link after 24 hours",
            "Add rate limiting to prevent abuse"
        ]
    },
    {
        "id": "PROJ-103",
        "type": "Bug",
        "title": "Login Page Crashes on Mobile",
        "description": "The login page throws a white screen error on iOS Safari when user submits the form",
        "priority": "High",
        "status": "In Progress",
        "story_points": 2,
        "assignee": "Arun Patel",
        "labels": ["bug", "mobile", "frontend"],
        "comments": [
            "Reproduced on iPhone 13 iOS 16",
            "Might be related to the form validation library version"
        ]
    },
    {
        "id": "PROJ-104",
        "type": "Story",
        "title": "User Registration",
        "description": "As a new user I want to create an account with name, email and password so that I can use the application",
        "priority": "High",
        "status": "To Do",
        "story_points": 8,
        "assignee": "Meena Reddy",
        "labels": ["frontend", "backend", "authentication"],
        "comments": [
            "Need email uniqueness validation",
            "Password strength requirements needed",
            "Should registration require email verification before login?"
        ]
    },
    {
        "id": "PROJ-105",
        "type": "Task",
        "title": "Email Verification System",
        "description": "Implement email verification flow after registration using tokenised verification links",
        "priority": "Medium",
        "status": "To Do",
        "story_points": 3,
        "assignee": "Kiran Singh",
        "labels": ["backend", "email"],
        "comments": [
            "Use existing email service",
            "Token should expire in 48 hours"
        ]
    },
    {
        "id": "PROJ-106",
        "type": "Task",
        "title": "Session Timeout Logic",
        "description": "Implement automatic session timeout after 30 minutes of inactivity for security compliance",
        "priority": "Low",
        "status": "To Do",
        "story_points": 2,
        "assignee": "Suresh Babu",
        "labels": ["backend", "security", "session"],
        "comments": [
            "Check compliance requirements for session duration",
            "Should warn user 5 minutes before timeout"
        ]
    },
    {
        "id": "PROJ-107",
        "type": "Bug",
        "title": "Duplicate Email Registration Allowed",
        "description": "System currently allows registration with same email twice causing duplicate accounts",
        "priority": "High",
        "status": "To Do",
        "story_points": 1,
        "assignee": "Raj Kumar",
        "labels": ["bug", "backend", "registration"],
        "comments": [
            "Critical bug found in UAT",
            "Quick fix needed before go-live"
        ]
    },
    {
        "id": "PROJ-108",
        "type": "Story",
        "title": "Remember Me Feature",
        "description": "As a user I want a remember me option on login so that I stay logged in for 30 days",
        "priority": "Low",
        "status": "To Do",
        "story_points": 2,
        "assignee": "Priya Sharma",
        "labels": ["frontend", "session", "authentication"],
        "comments": [
            "Use secure persistent cookie",
            "Should be disabled on shared devices warning"
        ]
    }
]

# ════════════════════════════════════════════════════════
# TOOLS — Agent uses these to collect data
# ════════════════════════════════════════════════════════

def get_all_tickets():
    """Returns all tickets as formatted text for AI to read"""
    result = "ALL JIRA TICKETS:\n"
    result += "=" * 60 + "\n"
    for t in jira_tickets:
        result += f"\nTicket ID:    {t['id']}\n"
        result += f"Type:         {t['type']}\n"
        result += f"Title:        {t['title']}\n"
        result += f"Description:  {t['description']}\n"
        result += f"Priority:     {t['priority']}\n"
        result += f"Status:       {t['status']}\n"
        result += f"Story Points: {t['story_points']}\n"
        result += f"Assignee:     {t['assignee']}\n"
        result += f"Labels:       {', '.join(t['labels'])}\n"
        result += f"Comments:     {' | '.join(t['comments'])}\n"
        result += "-" * 60 + "\n"
    return result

def get_tickets_by_type(ticket_type):
    """Returns only tickets of a specific type — Story, Bug or Task"""
    filtered = [t for t in jira_tickets if t['type'].lower() == ticket_type.lower()]
    if not filtered:
        return f"No tickets found of type: {ticket_type}"
    result = f"TICKETS OF TYPE '{ticket_type.upper()}':\n"
    result += "=" * 60 + "\n"
    for t in filtered:
        result += f"{t['id']} | {t['priority']} | {t['story_points']} pts | {t['title']}\n"
        result += f"  → {t['description'][:100]}...\n"
    return result

def get_high_priority_tickets():
    """Returns only high priority tickets"""
    filtered = [t for t in jira_tickets if t['priority'] == 'High']
    result = "HIGH PRIORITY TICKETS:\n"
    result += "=" * 60 + "\n"
    for t in filtered:
        result += f"{t['id']} | {t['type']} | {t['story_points']} pts | {t['title']}\n"
        result += f"  Status: {t['status']}\n"
        result += f"  {t['description'][:100]}\n\n"
    return result

def get_project_stats():
    """Returns overall project statistics"""
    total_points = sum(t['story_points'] for t in jira_tickets)
    by_type = {}
    by_priority = {}
    for t in jira_tickets:
        by_type[t['type']] = by_type.get(t['type'], 0) + 1
        by_priority[t['priority']] = by_priority.get(t['priority'], 0) + 1
    all_labels = []
    for t in jira_tickets:
        all_labels.extend(t['labels'])
    unique_labels = list(set(all_labels))
    result = f"""PROJECT STATISTICS:
Total Tickets:      {len(jira_tickets)}
Total Story Points: {total_points}
By Type:            {json.dumps(by_type)}
By Priority:        {json.dumps(by_priority)}
Tech Areas:         {', '.join(unique_labels)}
"""
    return result

# ════════════════════════════════════════════════════════
# TOOL REGISTRY
# ════════════════════════════════════════════════════════

tools = {
    "get_all_tickets":          get_all_tickets,
    "get_tickets_by_type_story": lambda: get_tickets_by_type("Story"),
    "get_tickets_by_type_bug":   lambda: get_tickets_by_type("Bug"),
    "get_tickets_by_type_task":  lambda: get_tickets_by_type("Task"),
    "get_high_priority_tickets": get_high_priority_tickets,
    "get_project_stats":         get_project_stats,
}

tools_description = """
You have access to these tools. Call them using JSON:
{"tool": "tool_name", "reason": "why you need this"}

Available tools:
- get_all_tickets:           Gets full details of every ticket
- get_tickets_by_type_story: Gets only Story tickets
- get_tickets_by_type_bug:   Gets only Bug tickets
- get_tickets_by_type_task:  Gets only Task tickets
- get_high_priority_tickets: Gets only High priority tickets
- get_project_stats:         Gets overall project statistics
- done:                      Call this after writing the final document
"""

# ════════════════════════════════════════════════════════
# THE AGENT
# ════════════════════════════════════════════════════════

def run_jira_agent():

    print("\n" + "=" * 60)
    print("  🤖 JIRA Requirements Analysis Agent")
    print("=" * 60)
    print(f"  Tickets loaded: {len(jira_tickets)}")
    print(f"  Total points:   {sum(t['story_points'] for t in jira_tickets)}")
    print("=" * 60)
    print("\n⚙️  Agent starting analysis...\n")

    agent_history = [
        {
            "role": "system",
            "content": f"""You are a senior Business Analyst AI agent specialising in requirements analysis.

Your job is to analyse Jira tickets and produce a professional Requirements Analysis Document.

{tools_description}

Work through these steps:
1. First get project statistics for an overview
2. Get all tickets for full details
3. Get high priority tickets to understand urgency
4. Get bugs separately to highlight risks
5. Once you have enough information write the FINAL DOCUMENT

The final document must start with exactly this text: REQUIREMENTS ANALYSIS DOCUMENT
And must include these sections:
1. Executive Summary
2. Functional Requirements
3. Technical Requirements  
4. Bug & Risk Analysis
5. Dependencies & Blockers
6. Recommended Sprint Plan
7. Open Questions

Be professional, thorough and concise. This document will be read by project managers and developers."""
        }
    ]

    collected_data = {}
    step = 0
    max_steps = 15

    while step < max_steps:
        step += 1

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=agent_history
        )

        agent_decision = response.choices[0].message.content.strip()

        agent_history.append({
            "role": "assistant",
            "content": agent_decision
        })

        # ── Check if agent wrote the final document ─────────
        if "REQUIREMENTS ANALYSIS DOCUMENT" in agent_decision:
            print("\n" + "=" * 60)
            print(agent_decision)
            print("\n" + "=" * 60)
            print("\n✅ Requirements Analysis Document generated!")

            # Save to a text file automatically
            with open("requirements_analysis.txt", "w") as f:
                f.write(agent_decision)
            print("📄 Document saved to: requirements_analysis.txt")
            break

        # ── Parse tool call ──────────────────────────────────
        try:
            clean = agent_decision.strip()
            if "```" in clean:
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            decision = json.loads(clean)
            tool_name = decision.get("tool")
            reason = decision.get("reason", "")

            print(f"🔧 Step {step}: Calling → {tool_name}")
            print(f"   Reason: {reason}")

            if tool_name == "done":
                print("\n✅ Agent completed!")
                break

            elif tool_name in tools:
                result = tools[tool_name]()
                collected_data[tool_name] = result
                print(f"   ✅ Done — {len(result)} characters of data retrieved")

                agent_history.append({
                    "role": "user",
                    "content": f"Tool result from {tool_name}:\n{result}\n\nContinue with your analysis. What do you need next?"
                })

            else:
                agent_history.append({
                    "role": "user",
                    "content": f"Tool '{tool_name}' not found. Please use one of the available tools."
                })

        except json.JSONDecodeError:
            print(f"   💭 Agent thinking...")
            agent_history.append({
                "role": "user",
                "content": "Please respond with a JSON tool call to continue, or write the REQUIREMENTS ANALYSIS DOCUMENT if you have enough information."
            })

# ── Run it! ──────────────────────────────────────────────
run_jira_agent()
