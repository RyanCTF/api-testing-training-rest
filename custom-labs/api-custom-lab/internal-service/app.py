"""Simulated internal-only service. Not published to the host in docker-compose.yml
- only reachable over the compose network. If this ever responds to you directly,
something on main-app fetched it server-side on your behalf.
"""
from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/internal/flag")
def flag():
    return (
        jsonify(
            {
                "flag": "FLAG{unsafe-consumption-1-solved}",
                "note": "This service has no published port - it's only reachable from inside "
                "the docker-compose network. Getting this response means main-app fetched "
                "this URL server-side on your behalf.",
            }
        ),
        200,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
