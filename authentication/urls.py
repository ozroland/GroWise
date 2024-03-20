from django.urls import path
from . import views
from django.views.generic import RedirectView

urlpatterns = [
    path('home', views.home, name='home'),
    path('signup', views.signup, name='signup'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('login', views.login, name='login'),
    path('signout', views.signout, name='signout'),
    path('', RedirectView.as_view(url='/home')),
]
