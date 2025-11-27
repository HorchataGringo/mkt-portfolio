import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

class EmailClient:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.username = os.environ.get('EMAIL_USER')
        self.password = os.environ.get('EMAIL_PASSWORD')
        self.enabled = bool(self.username and self.password)
        
        if not self.enabled:
            logging.warning("EMAIL_USER or EMAIL_PASSWORD not found. Email notifications disabled.")

    def send_email(self, subject, body, to_email, attachments=None):
        """Send an email with optional attachments."""
        if not self.enabled:
            logging.warning("Email client disabled. Skipping email.")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            if attachments:
                for filepath in attachments:
                    filename = os.path.basename(filepath)
                    with open(filepath, "rb") as f:
                        part = MIMEApplication(f.read(), Name=filename)
                    part['Content-Disposition'] = f'attachment; filename="{filename}"'
                    msg.attach(part)

            logging.info(f"Connecting to SMTP server {self.smtp_server}...")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logging.info(f"Email sent successfully to {to_email}.")
            return True

        except Exception as e:
            logging.error(f"Failed to send email: {e}")
            return False
