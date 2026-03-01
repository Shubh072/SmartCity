import os
import streamlit as st
from twilio.rest import Client
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables from .env file
load_dotenv()

def send_emergency_sms(message_body: str, to_phone: str = None) -> bool:
    """
    Sends an SMS using the Twilio API.
    
    Args:
        message_body: The text message to send.
        to_phone: The destination phone number (e.g., '+1234567890'). 
                  If None, attempts to use the TWILIO_DESTINATION_PHONE env var.
                  
    Returns:
        bool: True if sent successfully, False otherwise.
    """
    # Twilio credentials (try os.environ, then st.secrets for Streamlit Cloud)
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID') or st.secrets.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN') or st.secrets.get('TWILIO_AUTH_TOKEN')
    from_phone = os.environ.get('TWILIO_FROM_PHONE') or st.secrets.get('TWILIO_FROM_PHONE')
    
    # Fallback destination phone
    if not to_phone:
        to_phone = os.environ.get('TWILIO_DESTINATION_PHONE') or st.secrets.get('TWILIO_DESTINATION_PHONE')

    # Basic validation
    if not all([account_sid, auth_token, from_phone, to_phone]):
        print("Error: Missing Twilio credentials or destination phone number in environment variables.")
        return False

    try:
        client = Client(account_sid, auth_token)
        
        message = client.messages.create(
            body=message_body,
            from_=from_phone,
            to=to_phone
        )
        print(f"SMS Alert Dispatched! SID: {message.sid}")
        return True
    except Exception as e:
        print(f"Failed to send SMS: {e}")
        return False
        
def send_emergency_email(message_body: str, subject: str = "SMART CITY EMERGENCY ALERT", to_email: str = None) -> bool:
    """
    Sends an email using SMTP (e.g., Gmail).
    """
    smtp_server = os.environ.get('SMTP_SERVER') or st.secrets.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT') or st.secrets.get('SMTP_PORT', 587))
    sender_email = os.environ.get('SENDER_EMAIL') or st.secrets.get('SENDER_EMAIL')
    sender_password = os.environ.get('SENDER_PASSWORD') or st.secrets.get('SENDER_PASSWORD')
    
    if not to_email:
        to_email = os.environ.get('DESTINATION_EMAIL') or st.secrets.get('DESTINATION_EMAIL')
        
    if not all([sender_email, sender_password, to_email]):
        print("Error: Missing email credentials in environment variables.")
        return False
        
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(message_body, 'plain'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        print(f"Email Alert Dispatched to {to_email}!")
        return True
    except Exception as e:
        print(f"Failed to send Email: {e}")
        return False

if __name__ == "__main__":
    # Simple test execution
    success = send_emergency_sms("🚨 TEST ALERT: Smart City System Twilio Integration Operational")
    print("Test successful:", success)
