import os
import smtplib
from email.message import EmailMessage
import mimetypes


class EmailClient:

    def __init__(self):

        self.email_address = os.getenv('EMAIL_ADDRESS', '')
        if not self.email_address:
            print("ERROR: email address not provided in environment")

        self.email_password = os.getenv('EMAIL_PASSWORD', '')
        if not self.email_password:
            print("ERROR: email password not provided in environment")

        self.email_recipients = os.getenv('EMAIL_RECIPIENTS', '').split(",")
        if not self.email_recipients:
            print("ERROR: email recipients not provided in environment")

    def send_message(self, subject, text, attachments=[]):
        """Sending e-mail message.
        Parameters
        ----------
        subject: str
            subject of email
        text: str
            Body of email
        attachments : list od str, optional
            The list of files needed to be attached.
            Each attachment is represented by full file path (default is empty list])"""

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = 'Apache Logs Analyzer'
        msg['To'] = ', '.join(self.email_recipients)
        msg.set_content(str(text))
        msg.preamble = 'You will not see this in a MIME-aware mail reader.\n'

        for filePath in attachments:
            if not os.path.isfile(filePath):
                print(f'WARN: {filePath} is not a file!')
                continue

            ctype, encoding = mimetypes.guess_type(filePath)
            if ctype is None or encoding is not None:
                # No guess could be made, or the file is encoded (compressed), so
                # use a generic bag-of-bits type.
                ctype = 'application/octet-stream'

            maintype, subtype = ctype.split('/', 1)
            filename = filePath.split('/')[-1]

            with open(filePath, 'rb') as fp:
                msg.add_attachment(fp.read(), maintype=maintype, subtype=subtype, filename=filename)

        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(self.email_address, self.email_password)
            server.send_message(msg)
            server.close()
            print('Email sent!')

        except Exception as e:
            print('Something went wrong...')
            print(e)
