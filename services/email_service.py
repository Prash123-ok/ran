import smtplib # For sending emails
from email.mime.text import MIMEText # For creating email content
from email.mime.multipart import MIMEMultipart # For creating multipart emails
import os # For accessing environment variables
from dotenv import load_dotenv # For loading environment variables from a .env file

load_dotenv() # Load environment variables from .env file

def send_email(to_address, subject, body, dry_run=False): 
    """Send email using Gmail SMTP with environment-secured credentials or simulate in dry-run."""
    if dry_run: # If dry_run is True, simulate email sending without actually sending it
        print(f"📧 [DRY RUN] Email to {to_address} with subject '{subject}' would be sent here.")
        return True

    from_address = os.getenv("EMAIL_USER") # Get sender's email from environment variable
    password = os.getenv("EMAIL_PASS") # Get sender's email password from environment variable

    if not from_address or not password:
        print("Email credentials not found in environment variables.") # If credentials are not set, print an error message
        return False

    msg = MIMEMultipart() # Create a multipart email message
    msg["From"] = from_address # Set the sender's email address
    msg["To"] = to_address # Set the recipient's email address
    msg["Subject"] = subject # Set the email subject
    msg.attach(MIMEText(body, "plain")) # Attach the email body as plain text

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server: # Connect to Gmail's SMTP server using SSL
            server.login(from_address, password) # Log in to the SMTP server with the sender's credentials
            server.send_message(msg) # Send the email message
        print("📧 Confirmation email sent.") 
        return True # Return True if email was sent successfully
    except Exception as e: # Catch any exceptions that occur during the email sending process
        print(f"❌ Email sending failed: {e}") # Print the error message if email sending fails
        return False
