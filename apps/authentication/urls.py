from django.urls import path
from . import views
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy


urlpatterns = [
    path('home', views.home, name='home'),
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('signout', views.signout, name='signout'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('', RedirectView.as_view(url='/home')),
    path('profile/', views.profile, name='profile'),
    path("aszf/pdf/", views.download_terms_pdf, name="download_terms_pdf"),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='authentication/password_reset.html'), name='password_reset'),
    path('password_reset_done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
                                    template_name='authentication/password_reset_confirm.html',success_url=reverse_lazy('password_reset_complete')), name='password_reset_confirm'),
    path('reset/done/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('change_password/', views.change_password, name='change_password'),
]
