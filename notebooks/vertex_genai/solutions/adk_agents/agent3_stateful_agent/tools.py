# pylint: skip-file
from google.adk.tools.tool_context import ToolContext


def get_weather_stateful(city: str, tool_context: ToolContext) -> dict:
    """Retrieves weather, converts temp unit based on session state."""
    print(f"--- Tool: get_weather_stateful called for {city} ---")

    # --- Read preference from state ---
    preferred_unit = tool_context.state.get(
        "user:temperature_unit", "Celsius"
    )  # Default to Celsius
    print(
        f"--- Tool: Reading state 'user:temperature_unit': {preferred_unit} ---"
    )

    city_normalized = city.lower().replace(" ", "")

    # Mock weather data (always stored in Celsius internally)
    mock_weather_db = {
        "newyork": {"temp_c": 25, "condition": "sunny"},
        "london": {"temp_c": 15, "condition": "cloudy"},
        "tokyo": {"temp_c": 18, "condition": "light rain"},
    }

    if city_normalized in mock_weather_db:
        data = mock_weather_db[city_normalized]
        temp_c = data["temp_c"]
        condition = data["condition"]

        # Format temperature based on state preference
        if preferred_unit.capitalize() == "Fahrenheit":
            temp_value = (temp_c * 9 / 5) + 32  # Calculate Fahrenheit
            temp_unit = "°F"
        else:  # Default to Celsius
            temp_value = temp_c
            temp_unit = "°C"

        report = f"The weather in {city.capitalize()} is {condition} with a temperature of {temp_value:.0f}{temp_unit}."
        result = {"status": "success", "report": report}
        print(
            f"--- Tool: Generated report in {preferred_unit}. Result: {result} ---"
        )

        # Example of writing back to state (optional for this tool)
        tool_context.state["last_city_checked_stateful"] = city
        print(
            f"--- Tool: Updated state 'last_city_checked_stateful': {city} ---"
        )

        return result
    else:
        # Handle city not found
        error_msg = f"Sorry, I don't have weather information for '{city}'."
        print(f"--- Tool: City '{city}' not found. ---")
        return {"status": "error", "error_message": error_msg}


def set_user_preference(
    tool_context: ToolContext, preference: str, value: str
) -> dict:
    # Use 'user:' prefix for user-level state (if using a persistent SessionService)
    state_key = f"user:{preference}"
    tool_context.state[state_key] = value
    print(f"--- Tool: Set user preference '{preference}' to '{value}'")
    return {"status": "Preference updated"}


def say_hello(name: str = "there") -> str:
    """Provides a simple greeting, optionally addressing the user by name.

    Args:
        name (str, optional): The name of the person to greet. Defaults to "there".

    Returns:
        str: A friendly greeting message.
    """
    if name is None:
        name = "there"
    print(f"--- Tool: say_hello called with name: {name} ---")
    return f"Hello, {name}!"


def say_goodbye() -> str:
    """Provides a simple farewell message to conclude the conversation."""
    print(f"--- Tool: say_goodbye called ---")
    return "Goodbye! Have a great day."
