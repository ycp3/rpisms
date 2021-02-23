# pylint: disable=unsubscriptable-object

import smtplib
import imaplib
import base64
import email
from email.mime.text import MIMEText

# set to gmail email + password
username = "USERNAME@gmail.com"
password = "PASSWORD"

# only works for rogers phones, format: xxxxxxxxxx@pcs.rogers.com
phonemail = "PHONE_NUMBER@pcs.rogers.com"

# sends message to phone
def send(msg):
    smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    content = MIMEText(msg)
    content['subject'] = "RPSMS"
    content['from'] = username
    content['to'] = phonemail

    smtp_server.login(username, password)
    smtp_server.sendmail(username, phonemail, content.as_string())
    smtp_server.quit()

# checks gmail inbox for new messages and returns the content
# WILL ONLY WORK FOR TEXTS SENT TO EMAIL FROM A ROGERS PHONE NUMBER
def check():
    content = []
    imap_server = imaplib.IMAP4_SSL("imap.gmail.com")
    imap_server.login(username, password)
    imap_server.select('inbox')

    status, data = imap_server.search(None, 'ALL')

    if status != "OK":
        raise Exception

    mail_ids = []

    for block in data:
        mail_ids += block.split()

    for i in mail_ids:
        status, data = imap_server.fetch(i, '(RFC822)')

        for response_part in data:
            if isinstance(response_part, tuple):
                message = email.message_from_bytes(response_part[1])
                mail_from = message['from']
                # mail_subject = message['subject']

                if message.is_multipart():
                    mail_content = ''

                    for part in message.get_payload():
                        mail_content += part.get_payload()

                else:
                    mail_content = message.get_payload()

                # replace with 1(10 digit phone number)
                if mail_from == "PHONE_NUMBER@mms.rogers.com":
                    msg = base64.b64decode(mail_content.encode('ISO-8859-1')).decode('ISO-8859-1')
                    msg = msg.split(
                        "<!--/*SC*/ Content starts here /*EC*/-->")[1].split(
                            "<!--/*SC*/ Content ends here /*EC*/-->")[0].strip().strip("\n")
                    content.append(msg)
    return content

# wipes gmail inbox
def clearinbox():
    imap_server = imaplib.IMAP4_SSL("imap.gmail.com")
    imap_server.login(username, password)
    imap_server.select('inbox')
    
    status, data = imap_server.search(None, 'ALL')
    if status != "OK":
        raise Exception

    for num in data[0].split():
        imap_server.store(num, '+FLAGS', '\\Deleted')

    imap_server.expunge()
    imap_server.close()
    imap_server.logout()