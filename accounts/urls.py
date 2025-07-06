from django.urls import path
from .views import *

urlpatterns = [
    path("sendemail/",SendPasswordEmailView.as_view(), name="send-email"),
    path('register/',UserRegisterView.as_view(),name='register'),
    path('login/',UserLoginView.as_view(),name='login'),
    path('logout/',logout_view,name='logout'),
    path('reset-password/<uid>/<token>/',UserPasswordResetView.as_view(),name="reset-password")
]
