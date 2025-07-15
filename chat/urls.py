
from django.urls import path
from .views import *    
urlpatterns = [

    path('',index,name='index'),
    path('video/<str:room>/<str:created>/',video,name="video"),
    

    
]