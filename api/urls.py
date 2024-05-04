from django.urls import path
from . import views

urlpatterns = [
    path('receive_image', views.receive_image, name='receive_image'),
]