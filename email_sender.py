# email_sender.py (支持多收件人版)

import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
import config


def send_email(subject, content):
    """发送总结邮件，支持向一个或多个收件人发送。"""

    # 检查收件人列表是否为空
    if not config.RECEIVER_EMAILS:
        print("错误：收件人列表为空，无法发送邮件。")
        return

    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = formataddr(("每日深度分析", config.SENDER_EMAIL))

    # 【核心修改1】
    # 将收件人列表格式化为邮件头中显示的字符串，例如: "a@qq.com, b@163.com"
    message['To'] = ", ".join(config.RECEIVER_EMAILS)

    message['Subject'] = Header(subject, 'utf-8')

    try:
        print("正在连接邮件服务器...")
        smtp_ssl = smtplib.SMTP_SSL(config.EMAIL_HOST, config.EMAIL_PORT)
        smtp_ssl.login(config.SENDER_EMAIL, config.SENDER_AUTH_CODE)

        print(f"正在向 {len(config.RECEIVER_EMAILS)} 个收件人发送邮件...")

        # 【核心修改2】
        # sendmail函数的第二个参数正好需要一个包含所有收件人地址的列表
        smtp_ssl.sendmail(config.SENDER_EMAIL, config.RECEIVER_EMAILS, message.as_string())

        smtp_ssl.quit()
        print(f"邮件已成功发送。")
        print("收件人列表:", config.RECEIVER_EMAILS)

    except Exception as e:
        print(f"邮件发送失败，错误: {e}")

