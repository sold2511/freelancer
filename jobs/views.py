from django.shortcuts import render, HttpResponse, redirect
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import *
from django.views.generic import *
from rest_framework_simplejwt.tokens import AccessToken

from django.http import JsonResponse
from django.contrib.auth import get_user_model
# from rest_framework import token
from rest_framework import status
from django.contrib.auth.decorators import login_required

from accounts.serializers import *
from django.urls import reverse_lazy
from rest_framework.response import Response
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from django import forms
from django.db.models import Prefetch
from notification.models import Notification

# Create your views here.


def index(request):
    token = request.session.get('token')
    return Response(token)


class UserProfileView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'accounts/profile.html'
    context_object_name = 'users'

    def get_object(self):
        return self.request.user


def check_user_role(request):
    token = request.session.get('token')
    if not token:
        return Response(request, {'msg': "❌ No token found in session"})

    try:
        access_token = AccessToken(token)
        id = access_token.get('id')  # Use `.get()` to avoid KeyError

        if not id:
            return HttpResponse("⚠️ Token is valid but no user_id found")

        User = get_user_model()
        user = User.objects.get(id=id)
        print(user.role)

        return HttpResponse(f'role: {user.role} , token : {access_token}')

    except Exception as e:
        return Response(request, f"❌ Invalid or expired token: {str(e)}", status=status.HTTP_400_BAD_REQUEST)


def handle_login(req):
    if req.user.get_freelancer() or req.user.get_business():
        return redirect(reverse_lazy('freelancer-list'))
    return render(req, 'jobs/account_setup.html', {})


class JobListView(LoginRequiredMixin, ListView):
    model = Jobs
    template_name = 'jobs/job_list.html'
    context_object_name = 'matching_jobs'
    paginate_by = 5

    def get_queryset(self):
        user = self.request.user
        # this is a User instance

        if user.role == 'client':
            return Jobs.objects.filter(client_id=user.id)
        else:
            user_proposals = Proposal.objects.filter(freelancer=user)
            return Jobs.objects.filter(id__in=user_proposals.values_list('job_id', flat=True)).prefetch_related(Prefetch('proposal_set', queryset=user_proposals, to_attr='user_proposals'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.role != 'client':
            proposal_ids = user.proposal_set.values_list('job_id', flat=True)
            unmatched_jobs = Jobs.objects.exclude(id__in=proposal_ids)

            # Apply pagination manually for unmatched_jobs
            page = self.request.GET.get('unmatched_page')
            paginator = Paginator(unmatched_jobs, 5)  # 5 per page
            context['unmatching_jobs'] = paginator.get_page(page)

        return context


class JobCreateView(LoginRequiredMixin, CreateView):
    model = Jobs
    fields = ['title', 'description', 'budget',
              'deadline', 'category', 'attachments', 'skills']
    template_name = 'jobs/job_form.html'
    success_url = reverse_lazy('job-list')
    widgets = {
        'deadline': forms.DateInput(attrs={'type': 'date'}),
    }

    def form_valid(self, form):
        form.instance.client = self.request.user
        return super().form_valid(form)


class JobUpdateView(LoginRequiredMixin, UpdateView):
    model = Jobs
    fields = ['title', 'description', 'budget',
              'deadline', 'category', 'attachments', 'skills']
    template_name = 'jobs/job_form.html'
    success_url = reverse_lazy('job-list')

    def get_queryset(self):
        # Only allow the owner to update
        return Jobs.objects.filter(client_id=self.request.user)


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    fields = ['username', 'first_name', 'email', 'last_name', 'phone', 'tagline',
              'role', 'bio', 'profile_pic', 'website']  # Only status is editable
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('profile')

    def get_queryset(self):
        """Allow only the owner to update their profile."""
        print(self.request.user)
        return CustomUser.objects.filter(username=self.request.user)


class JobDeleteView(LoginRequiredMixin, DeleteView):
    model = Jobs
    template_name = 'jobs/job_confirm_delete.html'
    success_url = reverse_lazy('job-list')


class JobDetailView(LoginRequiredMixin, DetailView):
    model = Jobs
    template_name = 'jobs/job_detail.html'
    context_object_name = 'job'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job = self.get_object()
        user = self.request.user

        # Send proposals only if the user is the client of this job
        if user.role == 'client' and job.client == user:
            context['proposals'] = job.proposal_set.all()
        elif user.role == 'freelancer':
            # Check if this freelancer already submitted a proposal for this job
            context['my_proposal'] = job.proposal_set.filter(
                freelancer=user).first()

        return context


class ProposalCreateView(LoginRequiredMixin, CreateView):
    model = Proposal
    fields = ['message', 'estimated_budget', 'timeline']
    template_name = 'jobs/proposal_form.html'
    success_url = reverse_lazy('job-list')  # or back to detail page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job_id = self.kwargs['pk']
        context['job'] = Jobs.objects.get(pk=job_id)
        return context

    def form_valid(self, form):
        form.instance.freelancer = self.request.user
        form.instance.job_id = self.kwargs['pk']
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        # Prevent duplicate proposals
        if Proposal.objects.filter(job_id=kwargs['pk'], freelancer=request.user).exists():
            return HttpResponseForbidden("You have already submitted a proposal for this job.")
        return super().dispatch(request, *args, **kwargs)


class ProposalStatusUpdateView(LoginRequiredMixin, UpdateView):
    model = Proposal
    fields = ['status']  # Only status is editable
    template_name = 'jobs/proposal_status_form.html'

    def get_queryset(self):
        """Allow only the client who owns the job to update proposals."""
        return Proposal.objects.filter(job__client=self.request.user)

    def get_success_url(self):
        return reverse_lazy('job-detail', kwargs={'pk': self.object.job.pk})

    def form_valid(self, form):
        # you can add logic to notify the freelancer about the status change
        respomse = super().form_valid(form)
        proposal = form.instance
        freelancer = proposal.freelancer
        if form.cleaned_data['status'] == 'accepted':
            conversation, _ = Conversation.objects.get_or_create(
                proposal=proposal,
                client=form.instance.job.client,
                freelancer=freelancer,
                job=form.instance.job
            )

    # Always link the proposal, even if it already existed
            conversation.proposal = proposal
            conversation.save()
        send_mail(
            subject="🎉 Your Proposal Has Been Accepted!",
            message=f"Hello {freelancer.username},\n\nYour proposal for the job '{proposal.job.title}' has been accepted by the client.\nYou can now start a conversation or wait for further instructions.",
            from_email="dipanshusolanki131@gmail.com",
            recipient_list=[freelancer.email],
            fail_silently=False,
        )
        # ✅ Optional: Create In-App Notification
        Notification.objects.create(
            user=freelancer,
            message=f"Your proposal for '{proposal.job.title}' was accepted!",
            type='proposal',
            related_object=proposal,
        )
        return respomse


class ConversationListView(LoginRequiredMixin, ListView):
    model = Conversation
    template_name = 'chat/conversation_list.html'
    context_object_name = 'conversations'

    def get_queryset(self):
        return Conversation.objects.filter(models.Q(client=self.request.user) | models.Q(freelancer=self.request.user))


class ChatDetailView(LoginRequiredMixin, DetailView):
    model = Conversation
    template_name = 'chat/chat_detail.html'
    context_object_name = 'conversation'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.user != obj.client and request.user != obj.freelancer:
            return HttpResponseForbidden("❌ You are not part of this conversation.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = self.object.messages.order_by('timestamp')
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        conversation = self.object

        message_text = request.POST.get('message', '').strip()
        attachment = request.FILES.get('attachments')

        if message_text or attachment:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=message_text,
                attachments=attachment
            )

        return redirect(request.path)


class SendMessageView(LoginRequiredMixin, CreateView):
    model = Message
    fields = ['content']

    def form_valid(self, form):
        conversation = Conversation.objects.get(pk=self.kwargs['pk'])
        if self.request.user != conversation.client and self.request.user != conversation.freelancer:
            return HttpResponseForbidden("You can't send messages to this conversation.")

        form.instance.sender = self.request.user
        form.instance.conversation = conversation
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('chat-detail', kwargs={'pk': self.kwargs['pk']})


def upload_attachment(request):
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile
    if request.method == 'POST':
        uploaded_file = request.FILES.get('attachments')
        if uploaded_file:
            # Save file manually to media/ directory
            path = default_storage.save('message_attachments/' + uploaded_file.name, ContentFile(uploaded_file.read()))
            file_url = default_storage.url(path)
            return JsonResponse({
                'status': 'success',
                'file_name': uploaded_file.name,
                'file_url': file_url
            })
    return JsonResponse({'status': 'error'}, status=400)