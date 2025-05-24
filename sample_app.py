from flask import Flask, request, render_template, jsonify, redirect, url_for
from flask_cors import CORS
import requests
import json
import os
from datetime import datetime
import random
import uuid

app = Flask(__name__)
CORS(app)

# Configuration
app.config['DEBUG'] = True

# In-memory storage for interactive features (in production, use a database)
user_messages = []
todo_items = []
api_requests_log = []

class APIService:
    """Service class to handle various API integrations"""
    
    @staticmethod
    def get_weather_data(city="London"):
        """Get weather data from OpenWeatherMap API (free tier)"""
        try:
            # Log the API request
            api_requests_log.append({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "api": "Weather",
                "request": f"City: {city}",
                "id": str(uuid.uuid4())[:8]
            })
            
            # For demo purposes, return mock data (you can integrate real API later)
            weather_conditions = ["Clear sky", "Partly cloudy", "Overcast", "Light rain", "Sunny"]
            return {
                "city": city.title(),
                "temperature": round(random.uniform(15, 25), 1),
                "description": random.choice(weather_conditions),
                "humidity": random.randint(40, 80),
                "wind_speed": round(random.uniform(5, 20), 1),
                "status": "demo_data"
            }
        except Exception as e:
            return {
                "city": city,
                "temperature": 20.5,
                "description": f"Weather data unavailable: {str(e)[:50]}",
                "humidity": 65,
                "wind_speed": 10.0,
                "status": "error_demo"
            }
    
    @staticmethod
    def get_random_quote():
        """Get inspirational quote"""
        try:
            # Log the API request
            api_requests_log.append({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "api": "Quotes",
                "request": "Random quote",
                "id": str(uuid.uuid4())[:8]
            })
            
            # Extended quote collection
            quotes = [
                {"quote": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
                {"quote": "Innovation distinguishes between a leader and a follower.", "author": "Steve Jobs"},
                {"quote": "Life is what happens to you while you're busy making other plans.", "author": "John Lennon"},
                {"quote": "The future belongs to those who believe in the beauty of their dreams.", "author": "Eleanor Roosevelt"},
                {"quote": "It is during our darkest moments that we must focus to see the light.", "author": "Aristotle"},
                {"quote": "Success is not final, failure is not fatal: it is the courage to continue that counts.", "author": "Winston Churchill"},
                {"quote": "The way to get started is to quit talking and begin doing.", "author": "Walt Disney"},
                {"quote": "Don't let yesterday take up too much of today.", "author": "Will Rogers"},
                {"quote": "You learn more from failure than from success.", "author": "Unknown"},
                {"quote": "If you are working on something exciting, you don't have to be pushed.", "author": "Steve Jobs"}
            ]
            selected = random.choice(quotes)
            selected["status"] = "demo_data"
            return selected
        except Exception as e:
            return {
                "quote": "Error retrieving quote",
                "author": "System",
                "status": "error"
            }
    
    @staticmethod
    def get_random_user():
        """Get random user data"""
        try:
            # Log the API request
            api_requests_log.append({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "api": "Users",
                "request": "Random user profile",
                "id": str(uuid.uuid4())[:8]
            })
            
            first_names = ["Alice", "Bob", "Charlie", "Diana", "Edward", "Fiona", "George", "Hannah", "Ivan", "Julia"]
            last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
            companies = ["Tech Corp", "Innovation Ltd", "Future Systems", "Digital Solutions", "Smart Tech", "Cloud Nine", "Data Dynamics"]
            cities = ["New York", "London", "Tokyo", "Paris", "Sydney", "Toronto", "Berlin", "Amsterdam"]
            
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            
            return {
                "name": f"{first_name} {last_name}",
                "email": f"{first_name.lower()}.{last_name.lower()}@{random.choice(['gmail.com', 'yahoo.com', 'company.com'])}",
                "company": random.choice(companies),
                "city": random.choice(cities),
                "phone": f"+1-555-{random.randint(100,999)}-{random.randint(1000,9999)}",
                "status": "demo_data"
            }
        except Exception as e:
            return {
                "name": "Demo User",
                "email": "demo@example.com", 
                "company": "Demo Company Inc.",
                "city": "Demo City",
                "phone": "+1-555-000-0000",
                "status": "error_demo"
            }

# Initialize API service
api_service = APIService()

@app.route("/")
def home():
    """Main dashboard page"""
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
    
    # Get data from various APIs
    weather = api_service.get_weather_data("London")
    quote = api_service.get_random_quote()
    user = api_service.get_random_user()
    
    context = {
        "client_ip": client_ip,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "weather": weather,
        "quote": quote,
        "user": user,
        "total_messages": len(user_messages),
        "total_todos": len(todo_items),
        "recent_requests": api_requests_log[-5:] if api_requests_log else []
    }
    
    return render_template("index.html", **context)

@app.route("/api/health")
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.1.0",
        "services": ["weather", "quotes", "users", "messages", "todos", "requests_log"],
        "interactive_features": {
            "messages": len(user_messages),
            "todos": len(todo_items),
            "api_requests": len(api_requests_log)
        }
    })

@app.route("/api/weather/<city>")
def get_weather(city):
    """API endpoint to get weather for specific city"""
    weather_data = api_service.get_weather_data(city)
    return jsonify(weather_data)

@app.route("/api/quote")
def get_quote():
    """API endpoint to get random quote"""
    quote_data = api_service.get_random_quote()
    return jsonify(quote_data)

@app.route("/api/user")
def get_user():
    """API endpoint to get random user"""
    user_data = api_service.get_random_user()
    return jsonify(user_data)

# Interactive API Endpoints

@app.route("/api/messages", methods=["GET", "POST"])
def handle_messages():
    """Interactive messages API - users can post and view messages"""
    if request.method == "POST":
        data = request.get_json() if request.is_json else {}
        message_text = data.get("message", "").strip()
        author = data.get("author", "Anonymous").strip()
        
        if message_text:
            new_message = {
                "id": str(uuid.uuid4())[:8],
                "message": message_text,
                "author": author,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "ip": request.environ.get('REMOTE_ADDR', 'unknown')
            }
            user_messages.append(new_message)
            
            # Keep only last 50 messages
            if len(user_messages) > 50:
                user_messages.pop(0)
                
            return jsonify({"status": "success", "message": "Message posted successfully", "id": new_message["id"]}), 201
        else:
            return jsonify({"status": "error", "message": "Message text is required"}), 400
    
    # GET request - return all messages
    return jsonify({
        "messages": user_messages[-20:],  # Return last 20 messages
        "total_count": len(user_messages)
    })

@app.route("/api/todos", methods=["GET", "POST", "PUT", "DELETE"])
def handle_todos():
    """Interactive TODO API - users can manage their todo items"""
    if request.method == "POST":
        data = request.get_json() if request.is_json else {}
        task_text = data.get("task", "").strip()
        
        if task_text:
            new_todo = {
                "id": str(uuid.uuid4())[:8],
                "task": task_text,
                "completed": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "ip": request.environ.get('REMOTE_ADDR', 'unknown')
            }
            todo_items.append(new_todo)
            return jsonify({"status": "success", "todo": new_todo}), 201
        else:
            return jsonify({"status": "error", "message": "Task text is required"}), 400
    
    elif request.method == "PUT":
        data = request.get_json() if request.is_json else {}
        todo_id = data.get("id", "").strip()
        
        for todo in todo_items:
            if todo["id"] == todo_id:
                todo["completed"] = not todo["completed"]
                return jsonify({"status": "success", "todo": todo})
        
        return jsonify({"status": "error", "message": "Todo not found"}), 404
    
    elif request.method == "DELETE":
        data = request.get_json() if request.is_json else {}
        todo_id = data.get("id", "").strip()
        
        for i, todo in enumerate(todo_items):
            if todo["id"] == todo_id:
                removed_todo = todo_items.pop(i)
                return jsonify({"status": "success", "message": "Todo deleted", "todo": removed_todo})
        
        return jsonify({"status": "error", "message": "Todo not found"}), 404
    
    # GET request - return all todos
    return jsonify({
        "todos": todo_items,
        "total_count": len(todo_items),
        "completed_count": sum(1 for todo in todo_items if todo["completed"])
    })

@app.route("/api/requests-log")
def get_requests_log():
    """API endpoint to get recent API requests log"""
    return jsonify({
        "recent_requests": api_requests_log[-20:],  # Last 20 requests
        "total_requests": len(api_requests_log),
        "apis": {
            "weather": sum(1 for req in api_requests_log if req["api"] == "Weather"),
            "quotes": sum(1 for req in api_requests_log if req["api"] == "Quotes"), 
            "users": sum(1 for req in api_requests_log if req["api"] == "Users")
        }
    })

@app.route("/api/system-info")
def system_info():
    """API endpoint to get system information"""
    return jsonify({
        "hostname": os.environ.get("HOSTNAME", "unknown"),
        "python_version": "3.x",
        "flask_version": "2.3.3",
        "container_info": {
            "running_in_docker": os.path.exists("/.dockerenv"),
            "environment": "production" if not app.config['DEBUG'] else "development"
        },
        "interactive_stats": {
            "messages_count": len(user_messages),
            "todos_count": len(todo_items),
            "api_requests_count": len(api_requests_log)
        },
        "api_endpoints": [
            "/api/health",
            "/api/weather/<city>",
            "/api/quote", 
            "/api/user",
            "/api/messages (GET/POST)",
            "/api/todos (GET/POST/PUT/DELETE)",
            "/api/requests-log",
            "/api/system-info"
        ]
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found", "status": 404}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error", "status": 500}), 500

if __name__ == "__main__":
    print("🚀 Starting Enhanced Interactive Sample App...")
    print("📊 Available API endpoints:")
    print("   - GET / (Interactive dashboard)")
    print("   - GET /api/health (Health check)")
    print("   - GET /api/weather/<city> (Weather data)")
    print("   - GET /api/quote (Random quote)")
    print("   - GET /api/user (Random user)")
    print("   - GET/POST /api/messages (Interactive messages)")
    print("   - GET/POST/PUT/DELETE /api/todos (Interactive todo list)")
    print("   - GET /api/requests-log (API usage statistics)")
    print("   - GET /api/system-info (System information)")
    print(f"🌐 Server starting on http://0.0.0.0:5050")
    
    app.run(host="0.0.0.0", port=5050, debug=True)