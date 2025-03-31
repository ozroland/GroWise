from django.urls import path
from . import views
from django.views.generic import RedirectView


urlpatterns = [
    path('home', views.home, name='home'),
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('signout', views.signout, name='signout'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('', RedirectView.as_view(url='/home')),
    path('profile/', views.profile, name='profile'),
]
