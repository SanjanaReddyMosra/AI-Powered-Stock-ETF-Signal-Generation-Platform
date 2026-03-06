import smtplib
from email.mime.text import MIMEText


EMAIL = "your_email@gmail.com"
APP_PASSWORD = "your_app_password"


def send_email(email, stock, signal):

    message = f"""
Stock Alert 🚨

Stock: {stock}
Signal: {signal}

AI Powered Stock Signal Platform
"""

    msg = MIMEText(message)

    msg["Subject"] = "Stock Signal Alert"
    msg["From"] = EMAIL
    msg["To"] = email

    server = smtplib.SMTP("smtp.gmail.com", 587)

    server.starttls()
    server.login(EMAIL, APP_PASSWORD)

    server.send_message(msg)
    server.quit()