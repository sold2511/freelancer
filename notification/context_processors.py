# context_processors.py
from .models import Notification

def notification_context(request):
    if request.user.is_authenticated:
        return {
            "notifications": Notification.objects.filter(user=request.user).order_by("-created")[:5]
        }
    return {}
