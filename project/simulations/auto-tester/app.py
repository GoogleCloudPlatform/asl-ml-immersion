# /test [POST]
from flask import request, jsonify

from functions.run_testing_stages import run_testing_stages

@app.route('/run-test', methods=['POST'])
def run_test():
    data = request.get_json()
    
    golden_qa_bucket_uri = data.get('golden_qa_bucket_uri')
    testing_results = run_testing_stages(golden_qa_bucket_uri)
    if testing_results is None:
        return jsonify({"error": "Testing failed"}), 500
    
    # Logic to run the test based on test_id
    result = {"test_id": test_id, "status": "passed"}  # Placeholder result
    return jsonify(result)
