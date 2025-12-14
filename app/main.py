import json
import os
import logging
import sys
import time
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from app.services.user_service import UserService
from app.services.rabbitmq_service import init_rabbitmq, get_rabbitmq_service
from app.services.rabbitmq_consumer import start_rabbitmq_consumer

# Configure logging FIRST
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True  # Override any existing config
)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates')
CORS(app)

user_service = UserService()
rabbitmq_service = None
rabbitmq_connected = False

def init_message_broker():
    """Initialize RabbitMQ connection"""
    global rabbitmq_service, rabbitmq_connected
    
    logger.info("=" * 50)
    logger.info("Initializing RabbitMQ...")
    logger.info("=" * 50)
    
    # Call init_rabbitmq from rabbitmq_service module
    if init_rabbitmq(max_retries=10, retry_delay=2):
        rabbitmq_service = get_rabbitmq_service()
        rabbitmq_connected = True
        logger.info("✓ RabbitMQ initialized successfully")
        return True
    else:
        logger.warning("⚠ RabbitMQ initialization failed. App will run without message broker.")
        rabbitmq_connected = False
        return False

def publish_message(event_type, user_data):
    """Publish message to RabbitMQ"""
    if not rabbitmq_connected or not rabbitmq_service:
        logger.warning(f"Message broker not connected. Event '{event_type}' not published.")
        return False
    
    return rabbitmq_service.publish_event(event_type, user_data)

# --- Routes ---
@app.route('/')
def index():
    """Render index page"""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Service is running!",
        "rabbitmq_status": "connected" if rabbitmq_connected else "disconnected"
    }), 200

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    try:
        users = user_service.get_all_users()
        return jsonify(users), 200
    except Exception as e:
        logger.error(f"Error retrieving users: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user by ID"""
    try:
        user = user_service.get_user_by_id(user_id)
        if user:
            return jsonify(user), 200
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        logger.error(f"Error retrieving user: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Input validation
        required_fields = ['name', 'email']
        if not all(field in data for field in required_fields):
            return jsonify({"error": f"Missing required fields: {required_fields}"}), 400

        if not data.get('email') or '@' not in data['email']:
            return jsonify({"error": "Invalid email format"}), 400

        # Create user
        new_user = user_service.create_user(data)
        if not new_user:
            return jsonify({"error": "Failed to create user"}), 500

        # Publish message (non-blocking)
        publish_message('user_created', new_user)

        return jsonify({
            "message": "User created successfully",
            "user": new_user
        }), 201

    except Exception as e:
        logger.error(f"Error in create_user: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update a user"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Update user
        updated_user = user_service.update_user(user_id, data)
        if not updated_user:
            return jsonify({"error": "User not found"}), 404

        # Publish message (non-blocking)
        publish_message('user_updated', updated_user)

        return jsonify({
            "message": "User updated successfully",
            "user": updated_user
        }), 200

    except Exception as e:
        logger.error(f"Error in update_user: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    try:
        # Get user before deletion
        user = user_service.get_user_by_id(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Delete user
        deleted_user = user_service.delete_user(user_id)
        if not deleted_user:
            return jsonify({"error": "Failed to delete user"}), 500

        # Publish message (non-blocking)
        publish_message('user_deleted', deleted_user)

        return jsonify({
            "message": "User deleted successfully",
            "user": deleted_user
        }), 200

    except Exception as e:
        logger.error(f"Error in delete_user: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    logger.error(f"Server error: {error}")
    return jsonify({"error": "Internal server error"}), 500