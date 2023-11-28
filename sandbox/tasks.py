from django.core.mail import EmailMessage
from core.models import User
from django.template.loader import render_to_string
from celery import shared_task
from time import sleep


@shared_task
def send_email_to_all_user(message, context):
    print(f'message sending from {message}')

    email_list = [user.email for user in User.objects.all() if user.email]

    html_message = render_to_string('email/welcome.html', context)
    message = EmailMessage('subj', None, None, email_list)
    message.content_subtype = 'html'
    message.body = html_message
    message.attach_file('media/store/images/20230621_060448_0.jpg')
    message.send()

    print('message ware sent mesifkr926@gmail.com and marugithub@gmail.com successfully')


@shared_task
def print_message_for_every_5_sec(m, **kwargs):
    print('===============================================')
    print('message ware printed successfully')
    print(kwargs['name'])
    print('===============================================')
