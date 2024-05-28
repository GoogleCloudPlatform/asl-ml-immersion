""" Flask serving API and small demo UI.
"""
import logging

from flask import Flask, jsonify, request, send_file


app = Flask(__name__)


@app.route("/")
def _index():
    """Serve index.html in the static directory"""
    return send_file("static/index.html")


@app.route("/myapp", methods=["GET"])
def _answernaut():
    return jsonify({"answer": request.args["query"]})


@app.errorhandler(500)
def _server_error(e):
    """Serves a formatted message on-error"""
    logging.exception("An error occurred during a request.")
    return (
        f"An internal error occurred: <pre>{e}</pre><br>",
        500,
    )


if __name__ == "__main__":
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host="127.0.0.1", port=8080, debug=True)
