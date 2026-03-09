from groq import Groq
from dotenv import load_dotenv
import json

load_dotenv()
client = Groq()

# ════════════════════════════════════════════════
# TOOLS — These are like your Oracle stored procedures
# The agent DECIDES which ones to call
# ════════════════════════════════════════════════

def get_sales_data():
    """Returns sales data by department"""
    return """
    DEPARTMENT   | SALES   | REGION
    -------------|---------|-------
    Electronics  | 125,000 | North
    Clothing     | 45,000  | North
    Furniture    | 98,000  | South
    Sports       | 32,000  | South
    Electronics  | 140,000 | East
    Clothing     | 72,000  | East
    """

def get_employee_data():
    """Returns employee data by department"""
    return """
    DEPARTMENT   | EMPLOYEES | AVG_SALARY | AVG_EXPERIENCE
    -------------|-----------|------------|---------------
    Electronics  | 27        | 92,000     | 8 years
    Clothing     | 17        | 68,000     | 5 years
    Furniture    | 10        | 78,000     | 7 years
    Sports       | 6         | 62,000     | 4 years
    """

def get_target_data():
    """Returns target vs actual performance"""
    return """
    DEPARTMENT   | TARGET  | ACTUAL  | VARIANCE
    -------------|---------|---------|----------
    Electronics  | 220,000 | 265,000 | +45,000
    Clothing     | 150,000 | 117,000 | -33,000
    Furniture    | 90,000  | 98,000  | +8,000
    Sports       | 60,000  | 32,000  | -28,000
    """

def analyse_data(data, focus):
    """Sends data to AI for deep analysis"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a senior business analyst. Give clear, concise insights."
            },
            {
                "role": "user",
                "content": f"Analyse this data focusing on {focus}:\n{data}"
            }
        ]
    )
    return response.choices[0].message.content

# ════════════════════════════════════════════════
# TOOL REGISTRY — Agent looks here to find tools
# ════════════════════════════════════════════════

tools = {
    "get_sales_data": get_sales_data,
    "get_employee_data": get_employee_data,
    "get_target_data": get_target_data,
}

tools_description = """
You have access to these tools. Call them by responding ONLY with JSON like this:
{"tool": "tool_name", "reason": "why you need this tool"}

Available tools:
- get_sales_data: Gets sales figures by department and region
- get_employee_data: Gets employee count, salary and experience data
- get_target_data: Gets target vs actual performance and variance
- analyse_data: Use this when you have enough data to generate final analysis
- done: Use this when you have completed the full report
"""

# ════════════════════════════════════════════════
# THE AGENT BRAIN
# This is where the magic happens
# ════════════════════════════════════════════════

def run_agent(user_goal):

    print(f"\n🎯 Goal: {user_goal}")
    print("=" * 55)

    # Agent's memory
    agent_history = [
        {
            "role": "system",
            "content": f"""You are an intelligent Oracle Business Intelligence Agent.

{tools_description}

Your goal: {user_goal}

Work step by step:
1. Decide which tool you need first
2. Call it using JSON format
3. Look at the result
4. Decide if you need more data
5. When you have everything, call analyse_data then done

IMPORTANT: Respond ONLY with JSON when calling a tool.
When writing the final report, start with FINAL REPORT:"""
        }
    ]

    collected_data = {}  # Store all data collected by agent
    step = 0
    max_steps = 10  # Safety limit

    while step < max_steps:
        step += 1
        print(f"\n🤖 Agent Step {step}:")

        # Ask agent what to do next
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=agent_history
        )

        agent_decision = response.choices[0].message.content.strip()

        # Add agent's decision to history
        agent_history.append({
            "role": "assistant",
            "content": agent_decision
        })

        # ── Check if agent is done ──────────────────────────
        if "FINAL REPORT:" in agent_decision:
            print("\n" + "=" * 55)
            print(agent_decision)
            print("=" * 55)
            break

        # ── Try to parse agent's tool call ─────────────────
        try:
            # Clean the response and parse JSON
            clean = agent_decision.strip()
            if "```" in clean:
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            decision = json.loads(clean)
            tool_name = decision.get("tool")
            reason = decision.get("reason", "")

            print(f"   Calling tool: {tool_name}")
            print(f"   Reason: {reason}")

            # ── Execute the tool ────────────────────────────
            if tool_name == "done":
                print("\n✅ Agent completed the task!")
                break

            elif tool_name == "analyse_data":
                # Combine all collected data for analysis
                all_data = "\n\n".join([
                    f"{k}:\n{v}" for k, v in collected_data.items()
                ])
                result = analyse_data(all_data, user_goal)
                print(f"\n📊 Analysis complete!")

            elif tool_name in tools:
                # Call the requested tool
                result = tools[tool_name]()
                collected_data[tool_name] = result
                print(f"   ✅ Data retrieved successfully")

            else:
                result = f"Tool {tool_name} not found"

            # ── Feed tool result back to agent ──────────────
            agent_history.append({
                "role": "user",
                "content": f"Tool result from {tool_name}:\n{result}\n\nWhat do you want to do next?"
            })

        except json.JSONDecodeError:
            # Agent wrote something that isn't JSON
            # It might be thinking out loud — that's ok
            print(f"   💭 Agent thinking: {agent_decision[:80]}...")
            agent_history.append({
                "role": "user",
                "content": "Please respond with a JSON tool call to continue."
            })

    return collected_data


# ════════════════════════════════════════════════
# RUN THE AGENT
# ════════════════════════════════════════════════

print("=" * 55)
print("  My First Oracle AI Agent")
print("=" * 55)
print("\nWhat would you like the agent to do?")
print("Example: Give me a full business performance report")
print("Example: Find which departments need urgent attention")
print("Example: Analyse employee efficiency across departments")

goal = input("\nYour goal: ")
run_agent(goal)
