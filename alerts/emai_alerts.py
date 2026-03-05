import smtplib


def send_email(signal,stock,price):

    sender = "your_email@gmail.com"
    password = "your_app_password"

    receiver = "receiver_email@gmail.com"

    message = f"""
    Subject: Stock Signal Alert

    Stock: {stock}
    Signal: {signal}
    Predicted Price: {price}
    """

    server = smtplib.SMTP("smtp.gmail.com",587)

    server.starttls()

    server.login(sender,password)

    server.sendmail(sender,receiver,message)

    server.quit()