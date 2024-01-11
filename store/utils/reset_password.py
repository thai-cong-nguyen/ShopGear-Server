from datetime import datetime
from multiprocessing import Value
from pickle import TRUE
from django.core.mail import EmailMultiAlternatives, send_mail
from server.settings import EMAIL_HOST_USER
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
import os
import math, random
import secrets
def sendResetPasswordEmail(reset_password): 
    forgot_password_token = "{}".format(reset_password.get('key'))
    greetings = "Hi {}!".format(reset_password.get('username'))
    subject = "Password Reset for {title}".format(title="ShoGear App.") + str(datetime.now())
    message = "{greetings} Please use this Token for Reset Password on ShoGear App: {token}".format(greetings=greetings, token=forgot_password_token)
    recipient_list = [reset_password.get('email')]
    send_mail(subject=subject, from_email='uka.pgr@gmail.com', message=message, recipient_list=recipient_list, fail_silently=False)
    

def get_token_generator():
    return secrets.token_hex(2)