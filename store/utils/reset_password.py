from datetime import datetime
from pickle import TRUE
from django.core.mail import EmailMultiAlternatives, send_mail
from server.settings import EMAIL_HOST_USER
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
import os
import math, random

def sendResetPasswordEmail(reset_password_token):
    forgot_password_token = "{}".format(reset_password_token.get('key'))
    greetings = "Hi {}!".format(reset_password_token.get('username'))
    subject = "Password Reset for {title}".format(title="ShoGear App.") + str(datetime.now())
    message = "{greetings} Please use this Token for Reset Password on ShoGear App: {token}".format(greetings=greetings, token=forgot_password_token)
    recipient_list = [reset_password_token.get('email')]
    send_mail(subject= subject, from_email=os.getenv('EMAIL_HOST_USER'), message=message, recipient_list=recipient_list, fail_silently=True)

def get_token_generator():
    digits = "0123456789"
    OTP = ""
    for i in range(4) :
        OTP += digits[math.floor(random.random() * 10)]
    return OTP