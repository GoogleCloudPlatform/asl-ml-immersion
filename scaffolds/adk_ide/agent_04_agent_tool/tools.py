def get_pycon_events(event_city: str) -> dict:
    """Retrieves a list of PyCon events running this week for a specified city.

    Args:
        event_city (str): The name of the city (e.g., "New York", "London", "Tokyo").

    Returns:
        dict: A dictionary containing the event information.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes an 'events' key with a list of event details.
              If 'error', includes an 'error_message' key.
    """
    print(
        f"--- Tool: get_pycon_events called for city: {event_city}"
    )  # Log tool execution
    city_normalized = event_city.lower().replace(" ", "")  # Basic normalization

    # Mock events data
    mock_events_db = {
        "dublin": {
            "status": "success",
            "events": [
                {
                    "name": "PyCon Ireland 2025",
                    "date": "2025-11-15 - 2025-11-16",
                    "description": "The annual Python conference for Ireland",
                }
            ],
        },
        "online": {
            "status": "success",
            "events": [
                {
                    "name": "XtremePython 2025",
                    "date": "2025-11-18",
                    "description": "An upcoming online Python event.",
                }
            ],
        },
        "wroclaw": {
            "status": "success",
            "events": [
                {
                    "name": "PyCon Wroclaw 2025",
                    "date": "2025-11-15",
                    "description": "A PyCon event in Wrocław, Poland.",
                }
            ],
        }
    }

    if city_normalized in mock_events_db:
        # In a real tool, you would also filter by date_range here.
        return mock_events_db[city_normalized]
    else:
        return {
            "status": "error",
            "error_message": f"Sorry, I couldn't find any events for '{event_city}' during that time.",
        }