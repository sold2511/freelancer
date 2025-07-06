from django.contrib import admin
from .models import Jobs, Skill, Proposal, Conversation, Message
admin.site.register(Jobs)
admin.site.register(Skill)
admin.site.register(Proposal) 
admin.site.register(Conversation)
admin.site.register(Message)