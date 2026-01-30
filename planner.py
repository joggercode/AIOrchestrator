import re
from huggingface_hub import InferenceClient

HF_API_TOKEN = "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"  # your Hugging Face token
MODEL_ID = "microsoft/phi-3-mini-4k-instruct"

client = InferenceClient(model=MODEL_ID, token=HF_API_TOKEN)

def plan_workflow(user_input: str) -> str:
    prompt = f"""
    You are an expert orchestrator.
    Convert the following request into a structured workflow plan.
    Request: {user_input}
    Available APIs: flight_api, hotel_api, weather_api, activity_api, stock_api
    Output ONLY valid JSON with correct parameters from the request.
    """

    # ✅ Correct call: text_generation
    response = client.text_generation(
        prompt,
        max_new_tokens=256,
        return_full_text=False
    )

    return response

def extract_json(text: str) -> str:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON found in model output")
    return match.group(0)
