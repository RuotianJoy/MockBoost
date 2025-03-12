import random
import smtplib
from email.mime.text import MIMEText
from email.header import Header


def send_email(to_add):
    from_addr = '2750768449@qq.com'
    password = 'azbmhgkslrgvdebf'

    to_addr = to_add
    smtp_server = 'smtp.qq.com'

    # 邮件标题
    subject = "MockBoost验证码"
    code = random.randint(100000, 999999)

    # 邮件正文内容
    content = f"【MockBoost】您的验证码{code}，请勿泄漏于他人！"

    # 构建邮件内容
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = Header(from_addr)
    msg['To'] = Header(to_addr)
    msg['Subject'] = Header(subject)

    # 连接到 SMTP 服务器并发送邮件
    server = smtplib.SMTP_SSL(smtp_server, 465)
    server.login(from_addr, password)
    server.sendmail(from_addr, to_addr, msg.as_string())
    server.quit()
    return code


# send_email('liaojiongyi@gmail.com')

