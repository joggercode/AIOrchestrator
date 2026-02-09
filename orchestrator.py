from planner import plan_workflow, extract_json
from executor import execute_workflow
import json
import os

def main():
    user_input = input("Enter your request: ")
    workflow_raw = plan_workflow(user_input)
    print("Planned Workflow (RAW):", workflow_raw)

    try:
        workflow_json = extract_json(workflow_raw)
        results = execute_workflow(workflow_json)
        print("Final Results:", json.dumps(results, indent=2))

    except Exception as e:
        print("❌ Error while processing workflow:", str(e))
        print("Hint: Check if planner returned valid JSON. Raw output above shows what model generated.")

if __name__ == "__main__":
    main()

