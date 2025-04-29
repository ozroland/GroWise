from django.urls import path
from . import views

urlpatterns = [
    path('diseases/', views.disease_list, name='disease_list'),
    path('disease/<int:disease_id>/', views.disease_detail, name='disease_detail'),
    path('plants/', views.plant_list, name='plant_list'),
    path('plant/<int:plant_id>/', views.plant_detail, name='plant_detail'),
]
