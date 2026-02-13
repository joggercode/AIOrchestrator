import streamlit as st
import json
import pandas as pd
import datetime
from planner import plan_workflow, extract_json
from executor import execute_workflow, GLOBAL_CONTEXT

st.markdown(
    """
    <style>
    .stTextInput > div > div > input {
        border: 2px solid #000000 !important;
        border-radius: 6px;
        padding: 8px;
        font-weight: normal;
    }
    .stDataFrame table {
        border: 2px solid #000000 !important;
        border-collapse: collapse;
        width: 100%;
    }
    .stDataFrame th {
        background-color: #f2f2f2;
        font-weight: normal;
        border: 1px solid #000000;
        padding: 6px;
    }
    .stDataFrame td {
        border: 1px solid #000000;
        padding: 6px;
    }
    .stTextInput > div > div > input::placeholder { font-weight: 350; color: #888888; font-style: italic; }
    </style>
    """,
    unsafe_allow_html=True
)

st.set_page_config(page_title="AI Orchestrator Demo", layout="centered")

st.title("🛫 AI based API Orchestrator ")
user_input = st.text_input("Enter your request:", 
                           placeholder="e.g., Book me a flight from Delhi to Goa with hotel and sports activities")

if st.button("Generate Workflow"):
    if user_input.strip():
        GLOBAL_CONTEXT.clear()
        workflow_raw = plan_workflow(user_input)
        workflow = extract_json(workflow_raw)
        results = execute_workflow(workflow)

        st.session_state["results"] = results
        st.session_state["workflow"] = workflow

if "results" in st.session_state:
    results = st.session_state["results"]
    workflow = st.session_state["workflow"]

    # Flights Table
    if "flights" in results and isinstance(results["flights"], list):
        st.markdown("### ✈️ Top Flights")
        flights_df = pd.DataFrame(results["flights"])
        flights_df = flights_df.style.format({
            "price": "${:.0f}",
            "duration": "{}"
        }).highlight_min("price", color="lightgreen")
        st.dataframe(flights_df, use_container_width=True)

        # ✅ Calculate hotel check-in DATE as next day of booking date
        try:
            travel_dt_str = GLOBAL_CONTEXT.get("travel_datetime")
            if travel_dt_str:
                try:
                    base_dt = datetime.datetime.strptime(travel_dt_str, "%Y-%m-%d %H:%M")
                except ValueError:
                    base_dt = datetime.datetime.strptime(travel_dt_str, "%Y-%m-%d")

                check_in_date = (base_dt.date() + datetime.timedelta(days=0)).strftime("%Y-%m-%d")
                GLOBAL_CONTEXT["hotel_check_in"] = check_in_date
                GLOBAL_CONTEXT["weather_date"] = check_in_date

                wf_obj = json.loads(workflow)
                print(wf_obj)
                for step in wf_obj.get("workflow", []):
                    if step.get("api") == "hotel_api":
                        if "location" in step["parameters"]:
                            GLOBAL_CONTEXT["hotel_city"] = step["parameters"]["location"]
                        step["parameters"]["check_in"] = check_in_date
                        step["parameters"]["check_in_date"] = check_in_date
                    if step.get("api") == "weather_api":
                        if "location" in step["parameters"]:
                            GLOBAL_CONTEXT["weather_city"] = step["parameters"]["location"]
                        step["parameters"]["date"] = check_in_date
                    if step.get("api") == "activity_api":
                        if "location" in step["parameters"]:
                            GLOBAL_CONTEXT["activity_city"] = step["parameters"]["location"]
                        step["parameters"]["date"] = check_in_date
                workflow = json.dumps(wf_obj, indent=2)

                st.info(f"Hotel Check-in Date calculated: {check_in_date}")
        except Exception as e:
            st.error(f"Check-in calculation failed: {e}")
    else:
        st.warning(results.get("flights", "No flights found"))

    # Hotels Table
    if "hotels" in results:
        hotels_data = results["hotels"]
        city = GLOBAL_CONTEXT.get("hotel_city", "Unknown City")
        check_in = GLOBAL_CONTEXT.get("hotel_check_in", "Unknown Check-in")

        col1, col2 = st.columns(2)
        with col1: 
            st.text_input("Hotel check-out date (YYYY-MM-DD):", key="hotel_check_out")
        with col2: 
            st.text_input("Number of people:", key="num_people")    

        if not st.session_state.get("hotel_check_out") or not st.session_state.get("num_people"):
            st.info("Please enter hotel check-out date and number of people above.")
        else:
            GLOBAL_CONTEXT["hotel_check_out"] = st.session_state["hotel_check_out"]
            GLOBAL_CONTEXT["num_people"] = st.session_state["num_people"]

            try:
                check_in_date = datetime.datetime.strptime(check_in, "%Y-%m-%d")
                check_out_date = datetime.datetime.strptime(st.session_state["hotel_check_out"], "%Y-%m-%d")
                nights = (check_out_date - check_in_date).days
                if nights < 1:
                    nights = 1
            except Exception:
                nights = 1

            try:
                num_people = int(st.session_state["num_people"])
            except Exception:
                num_people = 1

            st.markdown(
                f"### 🏨 Hotel recommended for {city} ({check_in} till {st.session_state['hotel_check_out']}) "
                f"for {num_people} people ({nights} nights)"
            )

            if isinstance(hotels_data, dict) and "list" in hotels_data:
                hotels_list = []
                for h in hotels_data["list"]:
                    new_price = h["price"] * num_people * nights
                    hotels_list.append({
                        "name": h["name"],
                        "rating": h["rating"],
                        "price": new_price
                    })
                hotels_df = pd.DataFrame(hotels_list)
                hotels_df = hotels_df.style.format({
                    "price": "${:.0f}",
                    "rating": "{:.1f}"
                }).highlight_max("rating", color="lightblue")
                st.dataframe(hotels_df, use_container_width=True)
            elif isinstance(hotels_data, list) and hotels_data:
                hotels_df = pd.DataFrame(hotels_data)
                hotels_df = hotels_df.style.format({
                    "price": "${:.0f}",
                    "rating": "{:.1f}"
                }).highlight_max("rating", color="lightblue")
                st.dataframe(hotels_df, use_container_width=True)
            else:
                st.warning(f"⚠️ Hotels API did not return any results for {city}.")

    # Weather
    if "weather" in results:
        city = GLOBAL_CONTEXT.get("weather_city", "Unknown City")
        date = GLOBAL_CONTEXT.get("weather_date", "Unknown Date")
        st.markdown(f"### 🌤 Weather forecast for {city} on {date}")
        st.info(results["weather"])

    # Activities
    if "activities" in results:
        city = GLOBAL_CONTEXT.get("activity_city", "Unknown City")
        st.markdown(f"### 🎯 Suggested Activities in {city}")
        st.success(results["activities"])

    if st.session_state.get("hotel_check_out"):
        try:
            wf_obj = json.loads(workflow)
            for step in wf_obj.get("workflow", []):
                if step.get("api") == "hotel_api":
                    step["parameters"]["check_out_date"] = st.session_state["hotel_check_out"]
            workflow = json.dumps(wf_obj, indent=2)
        except Exception:
            pass

    st.subheader("API Calling Planned Workflow")
    st.json(json.loads(workflow))
