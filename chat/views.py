# from django.shortcuts import render
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.views.generic import ListView, DetailView
# from django.http import HttpResponseForbidden
# from .models import Conversation, Message
# from django.db import models
# from django.http import HttpResponse
# from django.views.generic.edit import CreateView
# from django.urls import reverse_lazy

# Create your views here.
# class ConversationListView(LoginRequiredMixin, ListView):
#     model = Conversation
#     template_name = 'chat/conversation_list.html'
#     context_object_name = 'conversations'

#     def get_queryset(self):
#         return Conversation.objects.filter(models.Q(client=self.request.user) | models.Q(freelancer=self.request.user))

# class ChatDetailView(LoginRequiredMixin, DetailView):
#     model = Conversation
#     template_name = 'chat/chat_detail.html'
#     context_object_name = 'conversation'

#     def dispatch(self, request, *args, **kwargs):
#         obj = self.get_object()
#         if request.user != obj.client and request.user != obj.freelancer:
#             return HttpResponseForbidden("❌ You are not part of this conversation.")
#         return super().dispatch(request, *args, **kwargs)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['messages'] = self.object.messages.order_by('timestamp')
#         return context

# class SendMessageView(LoginRequiredMixin, CreateView):
#     model = Message
#     fields = ['content']

#     def form_valid(self, form):
#         conversation = Conversation.objects.get(pk=self.kwargs['pk'])
#         if self.request.user != conversation.client and self.request.user != conversation.freelancer:
#             return HttpResponseForbidden("You can't send messages to this conversation.")

#         form.instance.sender = self.request.user
#         form.instance.conversation = conversation
#         return super().form_valid(form)

#     def get_success_url(self):
#         return reverse_lazy('chat-detail', kwargs={'pk': self.kwargs['pk']})
