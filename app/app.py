"""Minimal service deployed by the infrastructure demonstration."""

from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/")
def index():
    return jsonify(
        service="deployment-demo",
        project="automated-cloud-infrastructure-deployment-validation",
    )


@app.get("/health")
def health():
    return jsonify(status="healthy", service="deployment-demo")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
