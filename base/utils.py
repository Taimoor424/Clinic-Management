# base/utils.py

from django.core.mail import send_mail

def send_custom_email(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        from_email=None,  # uses DEFAULT_FROM_EMAIL in settings.py
        recipient_list=recipient_list,
        fail_silently=False,
    )
