from django.core.mail import EmailMessage
import os
import jwt
from django.conf import settings

class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['subject'],
            body=data['body'],
            from_email= os.environ.get('EMAIL_FROM'),
            to=[data['to_email']]
        )
        email.content_subtype = "html"
        email.send()
        
