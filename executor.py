import json
import requests

GLOBAL_CONTEXT = {}

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
        params = step.get("parameters", {})
        print(params)

        if api == "flight_api":
            origin = params.get("from") or params.get("origin")
            dest = params.get("to") or params.get("destination")
            route = f"{origin.title()}-{dest.title()}"
            # Save travel datetime for later hotel check-in calculation
            GLOBAL_CONTEXT["travel_datetime"] = params.get("date")
            if route in flights_data:
                flights = flights_data[route]["flights"]
                top_flights = sorted(flights, key=lambda x: x["price"])[:3]
                results["flights"] = top_flights
            else:
                results["flights"] = f"No flight data for {route}"
        
        elif api == "hotel_api":
            city = params.get("location") or params.get("city")
            if city and city in hotels_data:
                hotels = hotels_data[city]
                top_hotels = sorted(hotels, key=lambda x: x["rating"], reverse=True)[:3]
                results["hotels"] = {"list": top_hotels}
                # Save context for UI
                GLOBAL_CONTEXT["hotel_city"] = city
                GLOBAL_CONTEXT["hotel_check_in"] = params.get("check_in", "Unknown Check-in")
                GLOBAL_CONTEXT["hotel_check_out"] = params.get("check_out", "Unknown Check-out")
            else:
                results["hotels"] = f"No hotel data for {city}"

        elif api == "weather_api":
            location = params.get("location") or params.get("city")
            try:
                api_key = "93c319fd42459682e3a223a23217622a"  # replace with your real key
                url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
                resp = requests.get(url).json()

                if "weather" in resp and "main" in resp:
                    condition = resp["weather"][0]["main"]
                    temp = resp["main"]["temp"]
                    results["weather"] = f"{condition}, {temp}°C"
                    # Save context for UI
                    GLOBAL_CONTEXT["weather_city"] = location
                    GLOBAL_CONTEXT["weather_date"] = params.get("date", "Unknown Date")
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
            elif "Snow" in weather:
                results["activities"] = f"Indoor winter party or Snow Baseball in {location}"
            elif "Clear" in weather or "Sunny" in weather:
                results["activities"] = f"Outdoor cycling tour in {location}"
            elif "Haze" or "Smoke" in weather in weather:
                results["activities"] = f"Indoor sports game as Air Quality is not good in {location}"    
            else:
                results["activities"] = f"outdoor sports activity in {location}"

    return results
