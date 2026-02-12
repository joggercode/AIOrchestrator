import json
import streamlit as st
from api_registry import API_REGISTRY
from executor import GLOBAL_CONTEXT  # 👈 import global dict

class ContextBuilder:
    def __init__(self, user_input: str):
        self.user_input = user_input

    def build_context(self, workflow_json: str, results_so_far: dict) -> str:
        workflow = json.loads(workflow_json)["workflow"]

        for step in workflow:
            api = step["api"]
            params = step.get("params", {}) or step.get("parameters", {})
            required_params = API_REGISTRY.get(api, {}).get("params", [])

            # 🔹 Auto-fill from GLOBAL_CONTEXT if available
            for key in required_params:
                if key not in params or not params[key]:
                    if key in GLOBAL_CONTEXT:
                        params[key] = GLOBAL_CONTEXT[key]

            # 🔹 Prompt user only for missing params
            missing = [p for p in required_params if p not in params or not params[p]]
            if missing:
                st.warning(f"{api} is missing parameters: {', '.join(missing)}")
                for m in missing:
                    user_val = st.text_input(f"Please provide {m} for {api}:")
                    if user_val.strip():
                        params[m] = user_val.strip()
                        GLOBAL_CONTEXT[m] = user_val.strip()  # 👈 update global dict

            step["params"] = params

        return json.dumps({"workflow": workflow}, indent=2)
