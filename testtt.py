email_sender = "Kieuphuongkai@gmail.com"
email_receiver = "songco712@gmail.com"
email_password = "kqdifulobednqhym"
import os
import smtplib
from email.message import EmailMessage
import ssl
# email_password = os.environ.get("EMAIL_PASSWORD")

subject="Test Email"
body="This is a test email sent from Python by Kai"

em = EmailMessage()
em["From"] = email_sender
em["To"] = email_receiver
em["Subject"] = subject
em.set_content(body)

context = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
    smtp.login(email_sender, email_password)
    smtp.sendmail(email_sender, email_receiver, em.as_string())