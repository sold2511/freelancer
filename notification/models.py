from django.db import models
from accounts.models import CustomUser
from jobs.models import Proposal
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Create your models here.
class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField(max_length=100)
    is_seen = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True,null=True) 
    
    def __str__(self):
        return f"Notification to {self.user.username}: {self.message}"

    def save(self, *args, **kwargs):
        super(Notification,self ).save(*args, **kwargs)
        
        channel_layer = get_channel_layer()
        # notification_objs = Notification.objects.filter(is_seen=False).count()
        group_name = f"user_{self.user.id}"
        data = {
            'type': 'notification',
            'message': {
                'user_id': self.user.id,
                'message': self.message,
                'is_seen': self.is_seen,
            }
        }
        async_to_sync(channel_layer.group_send)(
             group_name,
            {
                "type": "notification_message",
                "message": self.message,
            }
        )
        
        
class DeviceToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    token = models.CharField(max_length=512, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.token[:20]}"
    