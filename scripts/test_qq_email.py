"""
Test QQ Mail SMTP Connection
"""

import os
import sys
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

def test_qq_mail():
    """Test QQ Mail SMTP with different methods"""

    smtp_server = os.getenv('EMAIL_SMTP_SERVER', 'smtp.qq.com')
    smtp_port = int(os.getenv('EMAIL_SMTP_PORT', '465'))
    username = os.getenv('EMAIL_USERNAME')
    password = os.getenv('EMAIL_PASSWORD')
    to_email = os.getenv('EMAIL_TO')

    print("=" * 70)
    print("Testing QQ Mail SMTP Connection")
    print("=" * 70)
    print(f"Server: {smtp_server}")
    print(f"Port: {smtp_port}")
    print(f"From: {username}")
    print(f"To: {to_email}")
    print()

    if not all([username, password, to_email]):
        print("❌ Error: Missing email configuration in .env")
        print(f"  EMAIL_USERNAME: {'✓' if username else '✗'}")
        print(f"  EMAIL_PASSWORD: {'✓' if password else '✗'}")
        print(f"  EMAIL_TO: {'✓' if to_email else '✗'}")
        return

    # Create test message
    msg = MIMEMultipart()
    msg['From'] = username
    msg['To'] = to_email
    msg['Subject'] = "Test Email from Blockchain Daily Bot"

    body = "This is a test email to verify SMTP connection."
    msg.attach(MIMEText(body, 'plain'))

    # Method 1: SMTP_SSL with default context
    print("Method 1: SMTP_SSL with default SSL context")
    print("-" * 70)
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            print("✓ SSL connection established")
            server.login(username, password)
            print("✓ Login successful")
            server.send_message(msg)
            print("✓ Email sent successfully!")
            return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        print()

    # Method 2: SMTP_SSL without context
    print("Method 2: SMTP_SSL without explicit context")
    print("-" * 70)
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            print("✓ SSL connection established")
            server.login(username, password)
            print("✓ Login successful")
            server.send_message(msg)
            print("✓ Email sent successfully!")
            return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        print()

    # Method 3: SMTP with STARTTLS (port 587)
    if smtp_port == 465:
        print("Method 3: Trying port 587 with STARTTLS instead")
        print("-" * 70)
        try:
            with smtplib.SMTP(smtp_server, 587) as server:
                server.starttls()
                print("✓ TLS enabled")
                server.login(username, password)
                print("✓ Login successful")
                server.send_message(msg)
                print("✓ Email sent successfully!")
                print()
                print("ℹ️  Note: Port 587 works! Update your .env:")
                print("   EMAIL_SMTP_PORT=587")
                return True
        except Exception as e:
            print(f"✗ Failed: {e}")
            print()

    # Method 4: Detailed SSL debugging
    print("Method 4: Detailed SSL debugging")
    print("-" * 70)
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        server = smtplib.SMTP_SSL(smtp_server, smtp_port, context=context)
        print("✓ SSL connection established (with CERT_NONE)")

        server.set_debuglevel(1)
        server.login(username, password)
        print("✓ Login successful")

        server.send_message(msg)
        print("✓ Email sent successfully!")
        server.quit()
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback
        print()
        print("Full traceback:")
        print(traceback.format_exc())

    return False

if __name__ == "__main__":
    success = test_qq_mail()

    print()
    print("=" * 70)
    if success:
        print("✅ Email test PASSED!")
    else:
        print("❌ Email test FAILED")
        print()
        print("Troubleshooting:")
        print("1. Verify QQ Mail authorization code (not QQ password)")
        print("2. Enable SMTP service in QQ Mail settings")
        print("3. Check if firewall is blocking port 465/587")
        print("4. Try using port 587 instead of 465")
