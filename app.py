import streamlit as st
import requests

# ════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ════════════════════════════════════════════════════════

st.set_page_config(
    page_title="HR Intelligence Agent",
    page_icon="🤖",
    layout="wide"
)

# ════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════

st.title("🤖 HR Intelligence Agent")
st.markdown("Ask anything about employees, salaries, departments or HR policies!")
st.divider()

# ════════════════════════════════════════════════════════
# SIDEBAR — Quick questions and info
# ════════════════════════════════════════════════════════

with st.sidebar:
    st.header("💡 Example Questions")
    st.markdown("""
    **Employee Data:**
    - Who are the highest paid employees?
    - Which department has the most staff?
    - Show me the top 10 earners
                
    **HR Policies:**
    - What is the bonus policy?
    - How many leave days do I get?
    - Can I work from home?
    
    **Combined:**
    - Which employees qualify for Band D salary?
    - Give me a full IT department report
    """)

    st.divider()
    st.header("🔌 API Status")

    # Check if API is running
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            st.success("✅ API Connected")
        else:
            st.error("❌ API Error")
    except:
        st.error("❌ API Offline — run python api.py first!")

# ════════════════════════════════════════════════════════
# CHAT INTERFACE
# ════════════════════════════════════════════════════════

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input at the bottom
if prompt := st.chat_input("Ask me anything about HR data or policies..."):

    # Show user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add to history
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # Call the API and show response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            try:
                response = requests.post(
                    "http://localhost:8000/ask",
                    json={"question": prompt}
                )

                if response.status_code == 200:
                    answer = response.json()["answer"]
                    st.markdown(answer)

                    # Add to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })
                else:
                    st.error("API returned an error. Please try again.")

            except Exception as e:
                st.error(f"Could not connect to API: {str(e)}")
                st.info("Make sure api.py is running in another terminal!")

# ════════════════════════════════════════════════════════
# BOTTOM — Clear chat button
# ════════════════════════════════════════════════════════

st.divider()
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
