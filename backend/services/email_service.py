"""Email service"""
from flask import current_app
from flask_mail import Message
from extensions import mail
from config import Config

class EmailService:
    """Service for sending emails"""
    
    def send_verification_email(self, recipient_email, verification_url):
        """Send email verification link"""
        try:
            msg = Message(
                subject="Verify your Revisify 2.0 account",
                recipients=[recipient_email],
                sender=Config.MAIL_FROM
            )
            msg.body = f"""
Welcome to Revisify 2.0!

Please verify your email address by clicking the link below:
{verification_url}

If you didn't create this account, please ignore this email.

Best regards,
Revisify 2.0 Team
"""
            msg.html = f"""
<h2>Welcome to Revisify 2.0!</h2>
<p>Please verify your email address by clicking the link below:</p>
<p><a href="{verification_url}">Verify Email</a></p>
<p>If you didn't create this account, please ignore this email.</p>
<p>Best regards,<br>Revisify 2.0 Team</p>
"""
            mail.send(msg)
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to send verification email: {str(e)}")
            return False

