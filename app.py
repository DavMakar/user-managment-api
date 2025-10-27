from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

class UserService:
    def __init__(self):
        self.users = [
            {"id": 1, "name": "John Doe", "email": "john@example.com", "role": "Developer"},
            {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "role": "Designer"},
            {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "role": "Manager"},
            {"id": 4, "name": "Alice Brown", "email": "alice@example.com", "role": "Developer"},
            {"id": 5, "name": "Charlie Wilson", "email": "charlie@example.com", "role": "Tester"}
        ]

    def get_all_users(self):
        return {"users": self.users, "count": len(self.users)}

    def get_user_by_id(self, user_id):
        return next((u for u in self.users if u["id"] == user_id), None)

    def create_user(self, data):
        new_user = {
            "id": len(self.users) + 1,
            "name": data.get("name", "Unknown"),
            "email": data.get("email", "unknown@example.com"),
            "role": data.get("role", "User")
        }
        self.users.append(new_user)
        return new_user

    def delete_user(self, user_id):
        user = self.get_user_by_id(user_id)
        if user:
            self.users = [u for u in self.users if u["id"] != user_id]
        return user

# Instantiate the service
user_service = UserService()

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "message": "Service is running!"})

@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify(user_service.get_all_users())

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = user_service.get_user_by_id(user_id)
    if user:
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.json
    new_user = user_service.create_user(data)
    return jsonify({"message": "User created successfully", "user": new_user}), 201

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    deleted_user = user_service.delete_user(user_id)
    if deleted_user:
        return jsonify({"message": "User deleted successfully", "user": deleted_user})
    return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)