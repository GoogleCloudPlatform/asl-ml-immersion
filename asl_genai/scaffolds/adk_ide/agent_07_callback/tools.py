# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
This is a mock weather tool that returns weather information
for a specified city and mock location tool that returns
 city name.
"""

import random


def get_location() -> dict[str, str]:
    """Retrieves the current location.

    Returns:
        dict: A dictionary containing the location information.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'report' key with location details.
              If 'error', includes an 'error_message' key.
    """
    city_list = ["New York", "London", "Tokyo", "Dublin"]
    current_city = random.choice(city_list)
    print(
        f"--- Tool: get_location called, current location is: {current_city}---"
    )  # Log tool execution
    return {
        "status": "success",
        "report": f"The current location is {current_city}",
    }


def get_weather(city: str) -> dict[str, str]:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city (e.g., "New York", "London", "Tokyo").

    Returns:
        dict: A dictionary containing the weather information.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'report' key with weather details.
              If 'error', includes an 'error_message' key.
    """
    print(
        f"--- Tool: get_weather called for city: {city} ---"
    )  # Log tool execution
    city_normalized = city.lower().replace(" ", "")  # Basic normalization

    # Mock weather data
    mock_weather_db = {
        "newyork": {
            "status": "success",
            "report": """
            The weather in New York is sunny with a temperature of 25°C.
            """,
        },
        "dublin": {
            "status": "success",
            "report": """
            Dublin is experiencing light rain and a temperature of 18°C.
            """,
        },
        "tokyo": {
            "status": "success",
            "report": """
            It's cloudy in Tokyo with a temperature of 15°C.
            """,
        },
    }

    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    else:
        return {
            "status": "error",
            "error_message": f"""
            Sorry, I don't have weather information for '{city}'.
            """,
        }
