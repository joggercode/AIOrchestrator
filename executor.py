import json
import requests

# Load JSON data once at the top
with open("database/flights.json") as f:
    flights_data = json.load(f)

with open("database/hotels.json") as f:
    hotels_data = json.load(f)

def execute_workflow(workflow_json: str):
    if not workflow_json.strip():
        raise ValueError("Planner returned empty workflow JSON")

    workflow = json.loads(workflow_json)["workflow"]
    results = {}

    for step in workflow:
        api = step["api"]
        params = step.get("parameters", {})  # 🔹 corrected to match planner output
        if api == "flight_api":
            origin = params.get("from") or params.get("origin").title()
            dest = params.get("to") or params.get("destination").title()
            route = f"{origin}-{dest}"
            if route in flights_data:
                flights = flights_data[route]["flights"]
                top_flights = sorted(flights, key=lambda x: x["price"])[:3]
                results["flights"] = top_flights
            else:
                results["flights"] = f"No flight data for {route}"

        elif api == "hotel_api":
            city = params.get("location") or params.get("city").title()
            if city in hotels_data:
                hotels = hotels_data[city]
                top_hotels = sorted(hotels, key=lambda x: x["rating"], reverse=True)[:3]
                results["hotels"] = top_hotels
            else:
                results["hotels"] = f"No hotel data for {city}"

        elif api == "weather_api":
            location = params.get("location", "Delhi")
            try:
                api_key = "93c319fd42459682e3a223a23217622a"  # 🔹 replace with your real key
                url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
                resp = requests.get(url).json()

                if "weather" in resp and "main" in resp:
                    condition = resp["weather"][0]["main"]
                    temp = resp["main"]["temp"]
                    results["weather"] = f"{condition}, {temp}°C"
                else:
                    results["weather"] = f"Weather API error: {resp}"
            except Exception as e:
                results["weather"] = f"Weather API failed: {e}"

        elif api == "activity_api":
            location = params.get("location", "Unknown")
            weather = results.get("weather", "Clear")

            if "Rain" in weather:
                results["activities"] = f"Indoor yoga class in {location}"
            elif "Clouds" in weather:
                results["activities"] = f"Indoor gym session in {location}"
            elif "Haze" in weather:
                results["activities"] = f"Indoor gym or tennis session as there is bit pollution in {location}"
            elif "Snow" in weather:
                results["activities"] = f"Indoor table tennis session in {location}"
            elif "Clear" in weather or "Sunny" in weather:
                results["activities"] = f"Outdoor cycling tour in {location}"
            else:
                results["activities"] = f"outdoor all sports activity in {location} Sports club"

    return results
