# app.py
#
# Phase H: minimal HTTP wrapper so Render's free web-service tier has
# something to route requests to. All actual logic still lives in
# main.py - this file's only job is to expose it over HTTP.

import os
from flask import Flask
from main import main

app = Flask(__name__)


@app.route("/process-tickets", methods=["POST"])
def process_tickets():
    main()  # runs the existing pipeline, prints to server logs
    return {"status": "done"}, 200


if __name__ == "__main__":
    # Render sets PORT via env var - must bind to 0.0.0.0, not localhost,
    # so traffic from outside the container can reach it.
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)