"""
Streamlit interface for the Acme Enterprise Operations Assistant.

The UI collects questions and displays the final response and MCP tool trace.
It does not directly read JSON files or invoke enterprise functions.
"""

import streamlit as st

from app.groq_agent import ask_enterprise_assistant

st.set_page_config(
    page_title="Acme Enterprise Assistant",
    page_icon=":briefcase:",
    layout="wide",
)

st.title("Acme Enterprise Operations Assistant")
st.write(
    "Ask questions about the simulated CRM, HR, ITSM, and company policy systems. "
    "The assistant uses Groq for tool selection and MCP for tool execution."
)

st.caption(
    "Learning demo: data is synthetic and tools are read-only. "
    "Do not enter real confidential or personal information."
)

question = st.text_area(
    "Your question",
    placeholder=(
        "Example: Find ABC Industries' account manager, its open incidents, "
        "and the Databricks access policy."
    ),
    height=110,
)

if st.button("Ask Assistant", type="primary"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        try:
            with st.spinner("Consulting enterprise systems..."):
                result = ask_enterprise_assistant(question)

            st.subheader("Assistant response")
            st.markdown(result["answer"])

            st.subheader("MCP tool execution trace")
            if not result["tool_trace"]:
                st.info("No MCP tools were called for this question.")

            for index, item in enumerate(result["tool_trace"], start=1):
                with st.expander(f"{index}. {item['tool']}", expanded=True):
                    st.markdown("**Arguments**")
                    st.json(item["arguments"])
                    st.markdown("**Tool result**")
                    st.code(item["result"], language="json")

        except Exception:
            st.error(
                "The request failed. Check that .env contains a valid Groq API key, "
                "the configured model is available, and the network is working."
            )
            st.info(
                "For detailed diagnostics, run the MCP tests and the Groq test "
                "from the VS Code terminal."
            )
