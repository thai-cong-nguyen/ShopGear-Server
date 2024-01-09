from datetime import datetime
from pickle import TRUE
from django.core.mail import EmailMultiAlternatives, send_mail
from server.settings import EMAIL_HOST_USER
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
import os

def sendResetPasswordEmail(reset_password_token):
    forgot_password_token = "{}".format(reset_password_token.key)
    greetings = "Hi {}!".format(reset_password_token.username)
    subject = "Password Reset for {title}".format(title="ShoGear App.") + str(datetime.now())
    message = "{greetings} Please use this Token for Reset Password on ShoGear App: {token}".format(greetings=greetings, token=reset_password_token)
    recipient_list = [reset_password_token.user.email]
    send_mail(subject= subject, message=message, recipient_list=recipient_list, fail_silently=True)