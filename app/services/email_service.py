import os
import logging
from mailersend import MailerSendClient
from mailersend import EmailBuilder
from mailersend.exceptions import MailerSendError

logger = logging.getLogger(__name__)

class EmailService:
    """Email service using MailerSend"""
    
    def __init__(self):
        self.api_key = os.getenv('MAILERSEND_API_TOKEN')
        self.sender_email = os.getenv('SENDER_EMAIL', 'noreply@test-nrw7gyme7z2g2k8e.mlsender.net')
        self.sender_name = os.getenv('SENDER_NAME', 'User Management System')
        self.client = None
        self.initialized = False
        
        if self.api_key:
            self.initialize()
    
    def initialize(self):
        """Initialize MailerSend client"""
        try:
            self.client = MailerSendClient(api_key=self.api_key)
            self.initialized = True
            logger.info("✓ MailerSend client initialized")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to initialize MailerSend: {e}")
            self.initialized = False
            return False
    
    def send_email(self, recipient_email, subject, text_body, html_body=None):
        """
        Send email using MailerSend
        
        Args:
            recipient_email (str): Recipient email address
            subject (str): Email subject
            text_body (str): Plain text email body
            html_body (str, optional): HTML email body
        
        Returns:
            bool: True if successful, False otherwise
        """
        
        if not self.initialized or not self.client:
            logger.warning("MailerSend not initialized. Email not sent.")
            return False
        
        try:
            # Build email
            email = (EmailBuilder()
                .from_email(self.sender_email, self.sender_name)
                .add_recipient(recipient_email)
                .subject(subject)
                .text(text_body)
            )
            
            # Add HTML body if provided
            if html_body:
                email = email.html(html_body)
            
            # Send email
            response = self.client.emails.send(email.build())
            
            logger.info(f"Email sent successfully to {recipient_email}")
            return True
        
        except MailerSendError as e:
            logger.error(f"MailerSend API Error: {e}")
            logger.error(f"Status Code: {e.status_code}")
            logger.error(f"Error Details: {e.details}")
            return False
        except Exception as e:
            logger.error(f"Error sending email to {recipient_email}: {e}")
            return False
    
    def send_email_template(self, recipient_email, template_id, variables=None):
        """
        Send email using MailerSend template
        
        Args:
            recipient_email (str): Recipient email address
            template_id (str): MailerSend template ID
            variables (dict, optional): Template variables
        
        Returns:
            bool: True if successful, False otherwise
        """
        
        if not self.initialized or not self.client:
            logger.warning("MailerSend not initialized. Email not sent.")
            return False
        
        try:
            email = (EmailBuilder()
                .from_email(self.sender_email, self.sender_name)
                .add_recipient(recipient_email)
                .template_id(template_id)
            )
            
            # Add template variables if provided
            if variables:
                for key, value in variables.items():
                    email = email.personalization(recipient_email, {key: value})
            
            response = self.client.emails.send(email.build())
            
            logger.info(f"Template email sent successfully to {recipient_email}")
            return True
        
        except MailerSendError as e:
            logger.error(f"MailerSend API Error: {e}")
            logger.error(f"Status Code: {e.status_code}")
            logger.error(f"Error Details: {e.details}")
            return False
        except Exception as e:
            logger.error(f"Error sending template email to {recipient_email}: {e}")
            return False

# Global email service instance
_email_service = None

def get_email_service():
    """Get or create email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service

def send_email(recipient_email, subject, text_body, html_body=None):
    """
    Convenience function to send email
    
    Usage:
        send_email("user@example.com", "Hello", "Plain text content", "<h1>HTML</h1>")
    """
    service = get_email_service()
    return service.send_email(recipient_email, subject, text_body, html_body)

def send_email_template(recipient_email, template_id, variables=None):
    """
    Convenience function to send template email
    
    Usage:
        send_email_template("user@example.com", "template_xyz", {"name": "John"})
    """
    service = get_email_service()
    return service.send_email_template(recipient_email, template_id, variables)