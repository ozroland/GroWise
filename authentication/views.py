from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth import authenticate as django_auth, login as django_login, logout as django_logout
from . tokens import generate_token
from .models import User


def home(request):
    return render(request, "home/home.html")

def signup(request):
    if request.method == "POST":
        email = request.POST['email']
        fname = request.POST['fname']
        lname = request.POST['lname']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
               
        if User.objects.filter(email=email).exists():
            messages.error(request, "Foglalt e-mail cím!!")
            return redirect('signup')
        
        if pass1 != pass2:
            messages.error(request, "A jelszavak nem egyeztek meg!!")
            return redirect('signup')
        
        myuser = User.objects.create_user(email, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False
        myuser.save()
        messages.success(request, "Sikeres létrehozás!!")
        
        return redirect('login')
        
        
    return render(request, "authentication/login.html")


def activate(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        # user.profile.signup_confirmation = True
        myuser.save()
        django_login(request,myuser)
        messages.success(request, "Sikeres létrehozás!!")
        return redirect('login')


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        pass1 = request.POST['pass1']
        
        user = django_auth(email=email, password=pass1)
        
        if user is not None:
            django_login(request, user)
            fname = user.first_name
            lname = user.last_name
            return render(request, "dashboard/dashboard.html",{"fname":fname, "lname":lname})
        else:
            messages.error(request, "Nem megfelelő adatok!!")
            return redirect('login')
    
    return render(request, "authentication/login.html")


def signout(request):
    django_logout(request)
    messages.success(request, "Sikeres kijelentkezés!!")
    return redirect('login')