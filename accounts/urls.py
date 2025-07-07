from django.urls import path
from .views import *

urlpatterns = [
    path('register/',UserRegisterView.as_view(),name='register'),
    path('',UserLoginView.as_view(),name='login'),
    path('logout/',logout_view,name='logout'),
    path('reset-password/<uid>/<token>/',UserPasswordResetView.as_view(),name="reset-password"),
    path('api/v1/verify-email/<uid>/<token>/',VerifiedUser.as_view(),name="reset-password")
]
