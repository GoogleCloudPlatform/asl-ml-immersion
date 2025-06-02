# tools.py for agent4_research_agent

def google_search(query: str) -> dict:
  """
  Performs a mock Google search for the given query.

  This tool simulates a Google search by returning predefined results
  for a few sample queries.

  Args:
    query: The search query string.

  Returns:
    A dictionary with the following keys:
      'status': 'success' if results are found, 'error' otherwise.
      'results': A list of strings representing search snippets (if successful).
      'error_message': A string describing the error (if unsuccessful).
  """
  print(f"google_search tool called with query: '{query}'")

  mock_results = {
      "what is the capital of france?": [
          "Paris is the capital and most populous city of France.",
          "The Eiffel Tower is a famous landmark in Paris.",
          "French is the official language of France."
      ],
      "python programming tutorial": [
          "Official Python documentation: www.python.org",
          "Real Python: Python Tutorials & Training",
          "Learn Python - Free Interactive Python Tutorial - Codecademy"
      ],
      "latest advancements in AI": [
          "Google AI Blog: Stay up-to-date with Google's AI research",
          "MIT Technology Review: Artificial Intelligence",
          "DeepMind: Advancing science through AI"
      ],
      "benefits of renewable energy": [
          "Renewable energy sources like solar and wind can reduce carbon emissions.",
          "Investing in renewable energy can create green jobs.",
          "Renewable energy can improve energy security."
      ],
      "impact of climate change on agriculture": [
          "Climate change can lead to crop failures due to extreme weather.",
          "Rising temperatures can affect livestock health and productivity.",
          "Changes in rainfall patterns can impact water availability for irrigation."
      ]
  }

  normalized_query = query.strip().lower()

  if normalized_query in mock_results:
    return {"status": "success", "results": mock_results[normalized_query]}
  else:
    # Try to find partial matches for demonstration
    for key_query, results in mock_results.items():
        if normalized_query in key_query or key_query in normalized_query:
            print(f"Note: Partial match found for '{query}'. Returning results for '{key_query}'")
            return {"status": "success", "results": results}
    return {"status": "error", "error_message": f"No results found for this mock query: '{query}'."}

if __name__ == '__main__':
  # Example Usage
  test_queries = [
      "what is the capital of France?",
      "python programming tutorial",
      "how to bake a cake", # This will be a miss
      "LATEST ADVANCEMENTS IN AI",
      "Renewable Energy" # This should find "benefits of renewable energy"
  ]

  for q in test_queries:
    print(f"\nSearching for: '{q}'")
    result = google_search(q)
    if result["status"] == "success":
      print("Results:")
      for i, res in enumerate(result["results"]):
        print(f"  {i+1}. {res}")
    else:
      print(f"Error: {result['error_message']}")

  unknown_query = "what is the weather like today?"
  print(f"\nSearching for: '{unknown_query}'")
  result = google_search(unknown_query)
  if result["status"] == "success":
      print("Results:")
      for i, res in enumerate(result["results"]):
        print(f"  {i+1}. {res}")
  else:
      print(f"Error: {result['error_message']}")
