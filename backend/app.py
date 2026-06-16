import os
import json
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import redis

app = Flask(__name__)

# ---------------------------------------------------------------------
# 1. DATABASE CONFIGURATION (PostgreSQL)
# ---------------------------------------------------------------------
# 'db' matches the service name you will use in your docker-compose.yml
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
DB_NAME = os.getenv("POSTGRES_DB", "task_db")
DB_HOST = os.getenv("POSTGRES_HOST", "db") 

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the Task model for PostgreSQL
class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)

    def to_dict(self):
        return {"id": self.id, "title": self.title}

# ---------------------------------------------------------------------
# 2. CACHE CONFIGURATION (Redis)
# ---------------------------------------------------------------------
# 'redis' matches the service name in your docker-compose.yml
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
cache = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

# ---------------------------------------------------------------------
# 3. API ENDPOINTS
# ---------------------------------------------------------------------

# Root Health Check
@app.route('/')
def index():
    return jsonify({"message": "Flask Backend API is running smoothly via Nginx!"})

# POST: Create Task (Saves to Database, Clears Cache)
@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({"error": "Missing 'title' in request body"}), 400

    # Save to PostgreSQL
    new_task = Task(title=data['title'])
    db.session.add(new_task)
    db.session.commit()

    # CRITICAL: Invalidate the Redis cache because the data changed!
    cache.delete('all_tasks')

    return jsonify(new_task.to_dict()), 210

# GET: Get Tasks (Checks Redis Cache first, falls back to DB)
@app.route('/tasks', methods=['GET'])
def get_tasks():
    # 1. Look for data in the Redis Cache
    cached_tasks = cache.get('all_tasks')
    
    if cached_tasks:
        print("--- Serving from Redis Cache ---")
        return jsonify(json.loads(cached_tasks))

    # 2. If Cache Miss, pull from PostgreSQL Database
    print("--- Cache Miss! Pulling from PostgreSQL ---")
    tasks = Task.query.all()
    tasks_list = [task.to_dict() for task in tasks]

    # 3. Save the database result to Redis Cache for next time (expires in 60 seconds)
    cache.setex('all_tasks', 60, json.dumps(tasks_list))

    return jsonify(tasks_list)

# ---------------------------------------------------------------------
# 4. INITIALIZATION & RUN
# ---------------------------------------------------------------------
if __name__ == '__main__':
    # Automatically create database tables if they don't exist
    with app.app_context():
        db.create_all()
        
    # In Docker, we bind to 0.0.0.0 so external containers (like Nginx) can reach it
    app.run(host='0.0.0.0', port=5000, debug=True)
    