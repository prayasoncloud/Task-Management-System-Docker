from flask import Flask
import redis
import psycopg2

app = Flask(__name__)

@app.route("/")
def home():
    return "Flask is running!"

@app.route("/health")
def health():
    return {
        "status": "ok"
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)