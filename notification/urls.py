from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('',index),
    path('send/' , send),
    path('save_token/', save_token),
    path('main/',main_view)
    
]



