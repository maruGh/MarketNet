import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketnet.settings')

celery = Celery('marketnet', broker='redis://localhost:6379/1')
celery.config_from_object('django.conf:settings', namespace='CELERY')
celery.autodiscover_tasks()
# celery.conf.broker_url = 'redis://localhost:6379/1'


# @celery.task(bind=True, ignore_result=True)
# def debug_task(self):
#     print(f'Request: {self.request!r}')
