from django.urls import path
from . import views

urlpatterns = [ 
    path('contact/', views.contact, name='contact'),
    path('info/disease', views.leaf_disease_info, name='leaf_disease_info'),
    path('info/plant', views.plant_identifier_info, name='plant_identifier_info'),
    path('info/database', views.plant_database_info, name='plant_database_info'),
    
]