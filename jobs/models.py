from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import CustomUser

# Create your models here
# User = CustomUser
# Create your models here.


class Jobs(models.Model):
    STATUS_CHOICES=[
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    CATEGORY_CHOICES = [
    ('web_dev', 'Web Development'),
    ('graphic_design', 'Graphic Design'),
    ('seo', 'SEO'),
    ('content_writing', 'Content Writing'),
    ('video_editing', 'Video Editing'),
    ('data_entry', 'Data Entry'),
    ('translation', 'Translation'),
    ('mobile_dev', 'Mobile App Development'),
    ('marketing', 'Digital Marketing'),
    ('support', 'Customer Support'),
    # Add more as needed
    ]
    title = models.CharField(max_length=255)
    description = models.TextField() 
    budget = models.DecimalField(max_digits=10, decimal_places=2) 
    deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posted_jobs')
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    attachments = models.FileField(upload_to='job_attachments/',)
    skills = models.ManyToManyField('Skill', blank=True)
    

    def __str__(self):
        return self.title
    
class Skill(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
    
class Proposal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    freelancer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    job = models.ForeignKey(Jobs, on_delete=models.CASCADE)
    message = models.TextField()
    estimated_budget = models.DecimalField(max_digits=10, decimal_places=2)
    timeline = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField( null=True)

    def __str__(self):
        return f'{self.freelancer.username} for {self.job.title}'

    def get_conversation(self):  
        return Conversation.objects.filter(client=self.job.client, freelancer=self.freelancer, job=self.job).first()


class Conversation(models.Model):
    proposal = models.OneToOneField('Proposal', on_delete=models.CASCADE, related_name='conversation', null=False, blank=True)
    client = models.ForeignKey(CustomUser, related_name='client_conversations', on_delete=models.CASCADE)
    freelancer = models.ForeignKey(CustomUser, related_name='freelancer_conversations', on_delete=models.CASCADE)
    job = models.ForeignKey('Jobs', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('client', 'freelancer', 'job')

    def __str__(self):
        return f"Chat: {self.client.username} & {self.freelancer.username} ({self.job.title})"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    attachments = models.FileField(upload_to='message_attachments/', null=True, blank=True , max_length=300)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:20]}"
