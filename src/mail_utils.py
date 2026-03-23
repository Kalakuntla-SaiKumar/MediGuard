"""
Email utilities for MediGuard
Handles sending password reset and notification emails
"""

from flask_mail import Message
import logging

logger = logging.getLogger(__name__)


def send_password_reset_email(mail, user_email, reset_token, app_url="http://localhost:5000"):
    """
    Send password reset email to user
    
    Args:
        mail: Flask-Mail instance
        user_email: User's email address
        reset_token: Password reset token
        app_url: Base URL of the application
    """
    try:
        reset_link = f"{app_url}/reset-password?token={reset_token}&email={user_email}"
        
        html_body = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; }}
                    .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    .header {{ color: #0D47A1; margin-bottom: 20px; }}
                    .content {{ color: #333; line-height: 1.6; }}
                    .button {{ display: inline-block; background-color: #1565C0; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
                    .footer {{ font-size: 12px; color: #666; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 15px; }}
                    .warning {{ background-color: #FFF3CD; border: 1px solid #FFC107; padding: 10px; border-radius: 4px; margin: 15px 0; color: #856404; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2 class="header">MediGuard - Password Reset Request</h2>
                    
                    <div class="content">
                        <p>Hello,</p>
                        <p>We received a request to reset your MediGuard account password. Click the button below to create a new password:</p>
                        
                        <center>
                            <a href="{reset_link}" class="button">Reset Password</a>
                        </center>
                        
                        <p>Or copy and paste this link in your browser:</p>
                        <p style="background: #f0f0f0; padding: 10px; border-radius: 4px; word-break: break-all;">
                            <code>{reset_link}</code>
                        </p>
                        
                        <div class="warning">
                            <strong>⚠️ Important:</strong> This link expires in 1 hour. If you didn't request this, ignore this email.
                        </div>
                        
                        <p><strong>Security Tips:</strong></p>
                        <ul>
                            <li>Never share your password with anyone</li>
                            <li>Always use a strong password (8+ characters)</li>
                            <li>Include uppercase, lowercase, numbers, and special characters</li>
                        </ul>
                    </div>
                    
                    <div class="footer">
                        <p>© 2026 MediGuard. All rights reserved.</p>
                        <p>This is an automated message, please do not reply to this email.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        text_body = f"""
        MediGuard - Password Reset Request
        
        Hello,
        
        We received a request to reset your MediGuard account password. 
        Click the link below to create a new password:
        
        {reset_link}
        
        This link expires in 1 hour. If you didn't request this, ignore this email.
        
        Security Tips:
        - Never share your password with anyone
        - Always use a strong password (8+ characters)
        - Include uppercase, lowercase, numbers, and special characters
        
        © 2026 MediGuard. All rights reserved.
        """
        
        msg = Message(
            subject='MediGuard - Password Reset Request',
            recipients=[user_email],
            html=html_body,
            body=text_body
        )
        
        mail.send(msg)
        logger.info(f"✓ Password reset email sent to: {user_email}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to send password reset email to {user_email}: {str(e)}")
        return False


def send_welcome_email(mail, user_email, username):
    """
    Send welcome email to new users
    
    Args:
        mail: Flask-Mail instance
        user_email: User's email address
        username: User's username
    """
    try:
        html_body = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; }}
                    .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    .header {{ color: #0D47A1; margin-bottom: 20px; }}
                    .content {{ color: #333; line-height: 1.6; }}
                    .button {{ display: inline-block; background-color: #1565C0; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
                    .footer {{ font-size: 12px; color: #666; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 15px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2 class="header">Welcome to MediGuard! 👋</h2>
                    
                    <div class="content">
                        <p>Hello {username},</p>
                        <p>Your MediGuard account has been created successfully! Your email (<strong>{user_email}</strong>) is now registered.</p>
                        
                        <p><strong>What Can You Do?</strong></p>
                        <ul>
                            <li>Check medication interactions (Drug-Drug, Drug-Food, Drug-Condition)</li>
                            <li>Get personalized safety recommendations</li>
                            <li>Save assessment history to your profile</li>
                            <li>Manage your health information</li>
                        </ul>
                        
                        <center>
                            <a href="http://localhost:5000/" class="button">Start Using MediGuard</a>
                        </center>
                        
                        <p>If you have any questions, feel free to contact our support team.</p>
                    </div>
                    
                    <div class="footer">
                        <p>© 2026 MediGuard. All rights reserved.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        msg = Message(
            subject='Welcome to MediGuard!',
            recipients=[user_email],
            html=html_body
        )
        
        mail.send(msg)
        logger.info(f"✓ Welcome email sent to: {user_email}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to send welcome email to {user_email}: {str(e)}")
        return False
