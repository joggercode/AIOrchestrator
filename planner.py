import boto3, json, re, requests

# Bedrock client setup
client = boto3.client("bedrock-runtime", region_name="us-east-1")

# Primary and fallback models
PRIMARY_MODEL = "deepseek.v3.2"
FALLBACK_MODEL = "qwen.qwen3-coder-next"


def plan_workflow(user_input: str) -> str:
    prompt = f"""
    You are an expert orchestrator.
    Convert the following request into a structured workflow plan.
    Request: {user_input}
    Available APIs: flight_api, hotel_api, weather_api, activity_api, stock_api
    Rules:
      - Always include weather_api when planning outdoor or sports activities.
      - Never leave origin or destination empty. If not specified, assume Delhi for origin and Mumbai for destination.
      - Output ONLY valid JSON with correct parameters from the request.
      - For flight_api, hotel_api, weather_api, and activity_api:
          * Always use FULL city names (e.g., "Delhi", "Mumbai") instead of airport codes or abbreviations.
          * Do not use IATA codes like DEL, BOM, JFK, etc.
    """

    try:
        response = client.invoke_model(
            modelId=PRIMARY_MODEL,
            body=json.dumps({
                "messages": [
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt}
                    ]}
                ],
                "max_tokens": 300,
                "temperature": 0.2
            })
        )
        output = response["body"].read().decode()
        return extract_json(output)

    except Exception:
        try:
            response = client.invoke_model(
                modelId=FALLBACK_MODEL,
                body=json.dumps({
                    "messages": [
                        {"role": "user", "content": [
                            {"type": "text", "text": prompt}
                        ]}
                    ],
                    "max_tokens": 300,
                    "temperature": 0.2
                })
            )
            output = response["body"].read().decode()
            return extract_json(output)
        except Exception:
            output = ollama_fallback(prompt)
            try:
                return extract_json(output)
            except:
                return local_fallback(user_input)


def ollama_fallback(prompt: str) -> str:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "mistral", "prompt": prompt}
    )
    output = ""
    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            if "response" in data:
                output += data["response"]
    return output


def local_fallback(user_input: str) -> str:
    origin_match = re.search(r"from\s+(\w+)", user_input, re.IGNORECASE)
    dest_match = re.search(r"to\s+(\w+)", user_input, re.IGNORECASE)
    activity_match = re.search(r"(sports|hiking|skiing|activities?)", user_input, re.IGNORECASE)

    origin = origin_match.group(1) if origin_match else "Unknown"
    destination = dest_match.group(1) if dest_match else "Unknown"
    activity = activity_match.group(1) if activity_match else "general"

    workflow = {
        "workflow": [
            {"api": "flight_api", "params": {"from": origin, "to": destination}},
            {"api": "hotel_api", "params": {"location": destination}},
            {"api": "weather_api", "params": {"location": destination}},
            {"api": "activity_api", "params": {"type": activity, "location": destination}}
        ]
    }
    return json.dumps(workflow, indent=2)


def extract_json(text: str) -> str:
    try:
        data = json.loads(text)

        # Case 1: Chat completion wrapper
        if "choices" in data:
            content = data["choices"][0]["message"]["content"].strip()
            if content.startswith("```json"):
                content = content[len("```json"):].strip()
            if content.endswith("```"):
                content = content[:-3].strip()
            parsed = json.loads(content)
            return json.dumps(parsed, indent=2)

        # Case 2: Direct workflow JSON
        elif "workflow" in data:
            return json.dumps(data, indent=2)

        else:
            raise ValueError("Unexpected response format")

    except Exception as e:
        raise ValueError(f"Failed to extract JSON: {e}\nRaw text: {text}")


if __name__ == "__main__":
    user_prompt = input("Enter your request: ")
    workflow = plan_workflow(user_prompt)
    print("\n=== Final Workflow ===")
    print(workflow)
