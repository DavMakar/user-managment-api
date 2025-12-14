import json
import logging
from threading import Thread
from app.services.rabbitmq_service import get_rabbitmq_service
from app.services.email_service import send_email

logger = logging.getLogger(__name__)

def handle_message(ch, method, properties, body):
    """Callback function to handle RabbitMQ messages"""
    try:
        message = json.loads(body)
        event_type = message.get('event_type')
        user_data = message.get('user_data', {})
        
        logger.info(f"Received message: {event_type}")
        
        # Route to appropriate handler
        if event_type == 'user_created':
            handle_user_created(user_data)
        elif event_type == 'user_updated':
            handle_user_updated(user_data)
        elif event_type == 'user_deleted':
            handle_user_deleted(user_data)
        
        # Acknowledge message
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info(f"Acknowledged message: {event_type}")
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def handle_user_created(user_data):
    """Handle user creation event"""
    try:
        email = user_data.get('email')
        name = user_data.get('name')
        
        logger.info(f"Processing user creation for {email}")
        
        subject = "Welcome to Our Platform"
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <h1 style="color: #333;">Welcome, {name}!</h1>
                    <p>Thank you for creating an account on our platform.</p>
                    <p>Your account has been successfully set up and is ready to use.</p>
                    <p>If you have any questions, feel free to contact our support team.</p>
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                    <p style="color: #666; font-size: 12px;">
                        Best regards,<br>
                        User Management System Team
                    </p>
                </div>
            </body>
        </html>
        """
        
        text_body = f"Hello {name},\n\nWelcome! Your account has been created successfully."
        
        send_email(email, subject, text_body, html_body=html_body)
        logger.info(f"Welcome email sent to {email}")
        
    except Exception as e:
        logger.error(f"Error handling user creation: {e}")

def handle_user_updated(user_data):
    """Handle user update event"""
    try:
        email = user_data.get('email')
        name = user_data.get('name')
        
        logger.info(f"Processing user update for {email}")
        
        subject = "Account Updated"
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <h1 style="color: #333;">Account Updated</h1>
                    <p>Hello {name},</p>
                    <p>Your account information has been successfully updated.</p>
                    <p>If you did not make this change, please contact our support team immediately.</p>
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                    <p style="color: #666; font-size: 12px;">
                        Best regards,<br>
                        User Management System Team
                    </p>
                </div>
            </body>
        </html>
        """
        
        text_body = f"Hello {name},\n\nYour account has been updated successfully."
        
        send_email(email, subject, text_body, html_body=html_body)
        logger.info(f"Update notification sent to {email}")
        
    except Exception as e:
        logger.error(f"Error handling user update: {e}")

def handle_user_deleted(user_data):
    """Handle user deletion event"""
    try:
        email = user_data.get('email')
        name = user_data.get('name')
        
        logger.info(f"Processing user deletion for {email}")
        
        subject = "Account Deleted"
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <h1 style="color: #d32f2f;">Account Deleted</h1>
                    <p>Hello {name},</p>
                    <p>We wanted to confirm that your account has been successfully deleted from our platform.</p>
                    <p>All your data has been removed from our systems.</p>
                    <p>If you have any questions or would like to reactivate your account, please contact our support team.</p>
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                    <p style="color: #666; font-size: 12px;">
                        Best regards,<br>
                        User Management System Team
                    </p>
                </div>
            </body>
        </html>
        """
        
        text_body = f"Hello {name},\n\nYour account has been deleted. If this was not intentional, please contact support."
        
        send_email(email, subject, text_body, html_body=html_body)
        logger.info(f"Deletion notification sent to {email}")
        
    except Exception as e:
        logger.error(f"Error handling user deletion: {e}")

def start_rabbitmq_consumer():
    """Start RabbitMQ consumer in background thread"""
    try:
        service = get_rabbitmq_service()
        
        if not service.connected:
            logger.warning("RabbitMQ not connected. Consumer will not start.")
            return False
        
        consumer_thread = Thread(
            target=service.consume_events,
            args=(handle_message,),
            daemon=True
        )
        consumer_thread.start()
        logger.info("✓ RabbitMQ consumer thread started")
        return True
        
    except Exception as e:
        logger.error(f"Failed to start RabbitMQ consumer: {e}")
        return False