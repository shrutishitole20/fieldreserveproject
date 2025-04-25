from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

@receiver(user_logged_in)
def send_login_notification(sender, request, user, **kwargs):
    subject = f'New Login Alert for {user.username}'
    message = f"""
    A user has logged into FieldReserve:
    
    Username: {user.username}
    Email: {user.email}
    First Name: {user.first_name}
    Last Name: {user.last_name}
    Login Time: {request.session.get('_auth_user_last_login', 'Unknown')}
    IP Address: {request.META.get('REMOTE_ADDR', 'Unknown')}
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [settings.SUPERUSER_EMAIL],
        fail_silently=False,
    )
