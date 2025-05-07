from django.urls import path
from . import views

urlpatterns = [
    path('<str:image_type>/', views.recognition, name='recognition'),
    path('evaluate/disease', views.evaluate_disease, name='evaluate_disease'),
    path('evaluate/plant', views.evaluate_plant, name='evaluate_plant'),
    path('delete', views.delete_images, name='delete_images'),
]
