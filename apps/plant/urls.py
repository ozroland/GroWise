from django.urls import path
from . import views

urlpatterns = [
    path('disease/', views.disease_list, name='disease'),
    path('plant/', views.plant_list, name='plant'),
]
