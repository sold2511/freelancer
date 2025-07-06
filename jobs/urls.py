from django.urls import path
from .views import *
urlpatterns = [
    path('profile/',UserProfileView.as_view(),name="profile"),
    path('profile/update/<int:pk>',UserProfileUpdateView.as_view(),name="profile-update"),
    path('account-setup/',handle_login,name="account-setup"),
    path('index/',check_user_role,name="index"),
    path('', JobListView.as_view(), name='job-list'),
    path('create/', JobCreateView.as_view(), name='job-create'),
    path('<int:pk>/update/', JobUpdateView.as_view(), name='job-update'),
    path('<int:pk>/delete/', JobDeleteView.as_view(), name='job-delete'),
    path('<int:pk>/', JobDetailView.as_view(), name='job-detail'),
    path('<int:pk>/propose/',ProposalCreateView.as_view(),name='proposal-create'),
    path('<int:pk>/propose/edit',ProposalStatusUpdateView.as_view(),name='proposal-edit-status'),
    path('chat', ConversationListView.as_view(), name='chat-list'),
    path('chat/<int:pk>/', ChatDetailView.as_view(), name='chat-detail'),
    path('chat/<int:pk>/send/', SendMessageView.as_view(), name='send-message'),
    
]
