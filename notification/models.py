from django.db import models
from accounts.models import CustomUser
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Create your models here.
class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    notificaiton = models.TextField(max_length=100)
    is_seen = models.BooleanField(default=False) 
    
    def save(self, *args, **kwargs):
        channel_layer = get_channel_layer()
        notification_objs = Notification.objects.all(is_seen=False).count()
        data = {
            'type': 'notification',
            'message': {
                'user_id': self.user.id,
                'notification': self.notificaiton,
                'is_seen': self.is_seen,
                'count': notification_objs
            }
        }
        async_to_sync(channel_layer.group_send)(
            
        )
        super(Notification,self ).save(*args, **kwargs)
        
class DeviceToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    token = models.CharField(max_length=512, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.token[:20]}"
    