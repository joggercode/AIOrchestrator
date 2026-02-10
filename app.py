import streamlit as st
import json
import pandas as pd
from planner import plan_workflow, extract_json
from executor import execute_workflow

st.markdown(
    """
    <style>
    /* Input box styling */
    .stTextInput > div > div > input {
        border: 2px solid #000000 !important;  /* bold black border */
        border-radius: 6px;
        padding: 8px;
        font-weight: bold;
    }

    /* Dataframe table styling */
    .stDataFrame table {
        border: 2px solid #000000 !important;
        border-collapse: collapse;
        width: 100%;
    }
    .stDataFrame th {
        background-color: #f2f2f2;
        font-weight: bold;
        border: 1px solid #000000;
        padding: 6px;
    }
    .stDataFrame td {
        border: 1px solid #000000;
        padding: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.set_page_config(page_title="AI Orchestrator Demo", layout="centered")


st.title("🛫 AI based API Orchestrator ")

user_input = st.text_input("Enter your request:")

if st.button("Generate Workflow"):
    if user_input.strip():
        workflow_raw = plan_workflow(user_input)
        workflow = extract_json(workflow_raw)
        results = execute_workflow(workflow)

        st.subheader("Planned Workflow")
        st.json(json.loads(workflow))

        st.subheader("Final Results")

        # Flights Table
        if "flights" in results and isinstance(results["flights"], list):
            st.markdown("### ✈️ Top Flights")
            flights_df = pd.DataFrame(results["flights"])
            flights_df = flights_df.style.format({
                "price": "${:.0f}",
                "duration": "{}"
            }).highlight_min("price", color="lightgreen")
            st.dataframe(flights_df, use_container_width=True)
        else:
            st.warning(results.get("flights", "No flights found"))

        # Hotels Table
        if "hotels" in results and isinstance(results["hotels"], list):
            st.markdown("### 🏨 Top Hotels")
            hotels_df = pd.DataFrame(results["hotels"])
            hotels_df = hotels_df.style.format({
                "price": "${:.0f}",
                "rating": "{:.1f}"
            }).highlight_max("rating", color="lightblue")
            st.dataframe(hotels_df, use_container_width=True)
        else:
            st.warning(results.get("hotels", "No hotels found"))

        # Weather
        if "weather" in results:
            st.markdown("### 🌤 Weather")
            st.info(results["weather"])

        # Activities
        if "activities" in results:
            st.markdown("### 🎯 Suggested Activities")
            st.success(results["activities"])
