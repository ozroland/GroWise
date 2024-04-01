from django.urls import path
from . import views

urlpatterns = [
    path('model_view', views.model_view, name='model_view'),
]
