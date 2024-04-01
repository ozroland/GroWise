from django.urls import path
from . import views

urlpatterns = [
    path('receive-operating-data', views.receive_operating_data, name='receive_operating_data'),
]