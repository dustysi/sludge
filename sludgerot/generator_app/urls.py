from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    # path('generate_video/', views.generate_video, name='generate_video'),
]
