from django.shortcuts import render, redirect
from django.http import JsonResponse

from django.contrib.auth.decorators import login_required
# from django.views.generic import ListView, DetailView
# from django.http import HttpResponseForbidden
from .models import *
from jobs.models import Conversation,Message
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





def index(request):
    if request.method == 'POST':
        room = request.POST['room']
        role = request.session.get('role')
        get_room = Chat.objects.filter(room_name=room)
        if get_room:
            c = get_room[0]
            number = c.allowed_users
            if int(number) < 2:
                number = 2
                if role=='client':
                    return redirect(f'/chat/video/{room}/created/')
                else:
                    return redirect(f'/chat/video/{room}/join/')
        else:
            create = Chat.objects.create(room_name=room, allowed_users=1)
            if create:
                return redirect(f'/chat/video/{room}/created/')
    


def video(request, room, created):
    return render(request, 'video.html', {'created': created, 'room': room})

@login_required
def upload_attachment(request):
    if request.method == 'POST':
        conversation_id = request.POST.get("room")
        file = request.FILES.get("attachments")
        if conversation_id and file:
            conv = Conversation.objects.get(id=conversation_id)
           
    return redirect("chat-detail", pk=conversation_id)



