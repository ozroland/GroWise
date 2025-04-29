from django.urls import path
from . import views

urlpatterns = [ 
    path('contact/', views.contact, name='contact'),
    path('diseaseinfo/', views.leaf_disease_info, name='leaf_disease_info'),
    path('plantinfo/', views.plant_identifier_info, name='plant_identifier_info'),
    path('databaseinfo/', views.plant_database_info, name='plant_database_info'),
    
]