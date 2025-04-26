import smtplib
from email.mime.text import MIMEText

def send_mail(receiver, subject, body):
    sender = "cloudplatform432@gmail.com"
    password = "gqqe yltw rjdg tjtx"
    
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
