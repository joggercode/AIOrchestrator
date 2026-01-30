# api_registry.py

"""
API Registry
------------
This file defines the available APIs for the orchestrator.
Each API entry contains:
- name: identifier used in workflows
- description: what the API does
- params: expected input parameters
"""

API_REGISTRY = {
    "flight_api": {
        "description": "Book flights between origin and destination cities.",
        "params": ["origin", "destination", "date"]
    },
    "hotel_api": {
        "description": "Reserve hotels at a given location.",
        "params": ["city", "check_in", "check_out"]
    },
    "weather_api": {
        "description": "Fetch weather forecast for a given city and date.",
        "params": ["city", "date"]
    },
    "activity_api": {
        "description": "Suggest sports or leisure activities based on location and weather.",
        "params": ["city", "weather"]
    },
    "stock_api": {
        "description": "Retrieve stock market data for a given ticker symbol.",
        "params": ["ticker", "date_range"]
    }
}

def list_apis():
    """Return all available APIs with descriptions."""
    return {name: meta["description"] for name, meta in API_REGISTRY.items()}

def get_api_info(api_name):
    """Return metadata for a specific API."""
    return API_REGISTRY.get(api_name, None)
