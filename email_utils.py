import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SENDER_EMAIL = "projectsendermail09@gmail.com"
APP_PASSWORD = "kpwyjpqxwijmelal"

def send_mail(subject, body, recipient):
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient, msg.as_string())

        return f"✅ Email successfully sent to {recipient}"

    except smtplib.SMTPException as e:
        return f"❌ Failed to send email: {str(e)}"
