from django.urls import path
from . import views

urlpatterns = [
    path('diseases/', views.disease_recognition, name='disease_recognition'),
    path('plants/', views.plant_recognition, name='plant_recognition'),
    path('evaluate/', views.evaluate_disease, name='evaluate_images'),
    path('evaluatep/', views.evaluate_plant, name='evaluate_plant'),
    path('delete/', views.delete_images, name='delete_images'),
]
