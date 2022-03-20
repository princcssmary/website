import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from platform import python_version

import pyotp


class EmailSender:
    def __init__(self, recipients=[''], cod=''):
        self.server = 'smtp.yandex.ru'
        self.user = 'digital.customs@yandex.ru'
        self.password = 'nfvj;yz1235789'
        self.mess = "Ваш код подтверждения: " + cod
        self.recipients = recipients
        self.sender = 'digital.customs@yandex.ru'
        self.subject = 'Подтверждение входа'
        self.text = self.mess
        self.html = '<html><head></head><body><p>' + self.text + '</p></body></html>'


    def start(self):
        self.msg = MIMEMultipart('alternative')
        self.msg['Subject'] = self.subject
        self.msg['From'] = 'Digital Customs <' + self.sender + '>'
        self.msg['To'] = ', '.join(self.recipients)
        self.msg['Reply-To'] = self.sender
        self.msg['Return-Path'] = self.sender
        self.msg['X-Mailer'] = 'Python/' + (python_version())

        part_text = MIMEText(self.text, 'plain')
        part_html = MIMEText(self.html, 'html')

        self.msg.attach(part_text)
        self.msg.attach(part_html)

    def send(self):
        self.mail = smtplib.SMTP_SSL(self.server)
        self.mail.login(self.user, self.password)
        self.mail.sendmail(self.sender, self.recipients, self.msg.as_string())
        self.mail.quit()


""" msg = EmailSender()
msg.start()
msg.send() """

