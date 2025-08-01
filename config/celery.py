import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


# @app.task(bind=True, ignore_result=True)
# def debug_task(self):
#     print(f'Request: {self.request!r}')
from django.core.mail import send_mail
@app.task
def sendmail(username,title,status,recipient):
    send_mail(
                subject=f"Your Proposal Has Been {status}!",
                message=f"Hello {username},\n\nYour proposal for the job '{title}' has been {status} by the client.",
                from_email="dipanshusolanki131@gmail.com",
                recipient_list=[recipient],
                fail_silently=False,
            )
    return 'mail send'