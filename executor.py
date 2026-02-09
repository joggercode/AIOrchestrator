import json
import requests


def execute_workflow(workflow_json: str):
    if not workflow_json.strip():
        raise ValueError("Planner returned empty workflow JSON")

    workflow = json.loads(workflow_json)["workflow"]
    results = {}

    for step in workflow:
        api = step["api"]
        params = step.get("parameters", {})

        if api == "flight_api":
            results["flight"] = f"Booked flight with params {params}"

        elif api == "hotel_api":
            results["hotel"] = f"Reserved hotel with params {params}"

        elif api == "weather_api":
            location = params.get("location", "Delhi")
            try:
                api_key = "93c319fd42459682e3a223a23217622a"  # 🔹 replace with your real key
                url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
                resp = requests.get(url).json()

                if "weather" in resp and "main" in resp:
                    condition = resp["weather"][0]["main"]   # e.g. Rain, Clear, Snow
                    temp = resp["main"]["temp"]
                    results["weather"] = f"{condition}, {temp}°C"
                else:
                    results["weather"] = f"Weather API error: {resp}"
            except Exception as e:
                results["weather"] = f"Weather API failed: {e}"

        elif api == "activity_api":
            location = params.get("location", "Unknown")
            weather = results.get("weather", "Clear")

            # Intelligent activity selection based on weather
            if "Rain" in weather:
                results["activities"] = f"Indoor yoga class in {location}"
            elif "Clouds" in weather:
                results["activities"] = f"Indoor gym session in {location}"
            elif "Snow" in weather:
                results["activities"] = f"Indoor table tennis session in {location}"
            elif "Clear" in weather or "Sunny" in weather:
                results["activities"] = f"Outdoor cycling tour in {location}"
            else:
                results["activities"] = f"Default outdoor activity in {location}"

    return results
