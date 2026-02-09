from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags






def send_account_activation_email(email,email_token,):
    subject = 'Verifiy Your Account Activation Email'
    message = f'please click your account activation email to activate your account\n\n\nhttp://127.0.0.1:8000/accounts/activate/{email_token}\n\n\n thank'
    
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    
    send_mail(subject, message, email_from ,recipient_list)
       
def send_email_verification_success(email):
    subject = 'Email Verified Successfully'
    message = 'Congratulations! Your email has been verified successfully. You can now log in to your account.'
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )