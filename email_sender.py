import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_CONFIG


class EmailSender:
    @staticmethod
    def send_email(subject, body):
        """
        发送邮件

        Args:
            subject: 邮件主题
            body: 邮件正文（HTML格式）

        Returns:
            bool: 发送成功返回True，否则返回False
        """
        try:
            message = MIMEMultipart()
            message["From"] = EMAIL_CONFIG["sender_email"]
            message["To"] = EMAIL_CONFIG["receiver_email"]
            message["Subject"] = subject
            message.attach(MIMEText(body, "html"))

            with smtplib.SMTP_SSL(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as server:
                server.login(EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["password"])
                server.send_message(message)
            print(f"邮件发送成功: {subject}")
            return True
        except Exception as e:
            print(f"邮件发送失败: {e}")
            return False
