import imaplib
import smtplib
from email.header import Header
from email.mime.text import MIMEText


class IMAPReceiver:
    def __init__(self):
        self.email_account = "chaochinghua@vip.qq.com"
        self.email_passwd = "hrivilxiymkzbdeg"
        self.imap_server_host = "imap.qq.com"
        self.imap_server_port = 993

    def __enter__(self):
        try:
            # 如果服务器不使用SSL，则将IMAP4_SSL 改成IMAP4
            self.email_server = imaplib.IMAP4_SSL(host=self.imap_server_host,
                                                  port=self.imap_server_port)
        except Exception:
            print("连结IMAP服务器出现了问题")
            exit(1)
        try:
            self.email_server.login(self.email_account, self.email_passwd)
        except Exception:
            print("登入IMAP服务器出现了问题")
            exit(1)

        self.email_server.select()
        email_count = len(self.email_server.search(None, 'ALL')[1][0].split())
        typ, email_content = self.email_server.fetch(f'{email_count}'.encode(),
                                                     '(RFC822)')

        email_content = email_content[0][1].decode()
        return email_content

    def __exit__(self, exc_type, exc_value, trace_back_info):
        self.email_server.close()
        self.email_server.logout()


class STMPSender:
    def __init__(self):
        self.email_account = "chaochinghua@vip.qq.com"
        self.email_passwd = "hrivilxiymkzbdeg"
        self.smtp_server_host = "smtp.qq.com"
        self.smtp_server_port = 465
        self.receiver, self.subject, self.context = None, None, None

    def __call__(self,
                 receiver: str = "",
                 subject: str = "",
                 context: str = ""):
        self.receiver = receiver
        self.subject = subject
        self.context = context
        # 如果服务器不支持SSL，则将SMTP_SSL 改成SMTP
        self.email_client = smtplib.SMTP_SSL(self.smtp_server_host,
                                             self.smtp_server_port)

    def __enter__(self):
        # 如果要发送html，将plain改为html
        self.message = MIMEText(self.context, 'plain', 'utf-8')
        # 设定发件人、收件人和主题
        self.message["From"] = Header(self.email_account, "utf-8")
        self.message["To"] = Header(self.receiver, "utf-8")
        self.message["Subject"] = Header(self.subject, "utf-8")
        try:
            self.email_client.login(self.email_account, self.email_passwd)
        except Exception:
            print("登入邮箱出现了错误")
        else:
            pass
        finally:
            return self.email_client, self.message

    def __exit__(self, exc_type, exc_value, trace_back_info):
        self.email_client.close()


if __name__ == "__main__":
    email_context = "这是一则使用Python 自动发送的邮件"
    client = STMPSender()
    client("893035651@qq.com", "使用Python发送的测试邮件", email_context)
    with client as (mail_client, message):
        mail_client.sendmail(client.email_account, client.email_account,
                             message.as_string())
        print(f"邮件发送到 {client.email_account} 成功")

    receiver = IMAPReceiver()
    with receiver as content:
        print(content)
