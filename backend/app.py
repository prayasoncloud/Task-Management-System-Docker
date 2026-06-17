from flask import Flask
import redis
import psycopg2

app = Flask(__name__)

@app.route("/")
def home():
    return "Flask is running!"

@app.route("/health")
def health():
    return {"status": "ok"}

@app.route("/db")         
def db_check():
    conn = psycopg2.connect(
        host="postgres",
        database="taskdb",
        user="admin",
        password="password"
    )
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    cur.close()
    conn.close()
    return str(version)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)