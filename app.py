import streamlit as st
import json
from planner import plan_workflow, extract_json
from executor import execute_workflow

st.set_page_config(page_title="AI Orchestrator Demo", layout="centered")

st.title("🛫 AI Orchestrator Demo")

user_input = st.text_input("Enter your request:")

if st.button("Generate Workflow"):
    if user_input.strip():
        workflow_raw = plan_workflow(user_input)
        workflow = extract_json(workflow_raw)
        results = execute_workflow(workflow)

        st.subheader("Planned Workflow")
        st.json(json.loads(workflow))

        st.subheader("Final Results")
        st.json(results)
