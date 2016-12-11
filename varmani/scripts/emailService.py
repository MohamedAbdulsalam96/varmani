import smtplib
import json

class EmailService(object):
    def __init__(self):
        accessDetails = open('/home/hemant/access.txt')
        aD = json.loads(accessDetails.read())
        self.session = smtplib.SMTP('smtp.gmail.com', 587)
        self.session.ehlo()
        self.session.starttls()
        self.username = aD['gmail_username']
        self.password = aD['gmail_password']
        self.session.login(self.username, self.password)

    def sendMessage(self,email_subject, body_of_email, recipient):
        headers = "\r\n".join(["from: " + self.username,
                       "subject: " + email_subject,
                       "to: " + recipient,
                       "mime-version: 1.0",
                       "content-type: text/html"])

        # body_of_email can be plaintext or html!
        content = headers + "\r\n\r\n" + body_of_email
        self.session.sendmail(self.username, recipient, content)