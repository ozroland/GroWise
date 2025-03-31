from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth import authenticate as django_auth, login as django_login, logout as django_logout
from . tokens import generate_token
from .models import User
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.decorators import login_required


def home(request):
    if request.user.is_authenticated:
        return redirect('disease_recognition')
    else:
        return render(request, "core/home.html")


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

        token = generate_token.make_token(myuser)
        uidb64 = urlsafe_base64_encode(force_bytes(myuser.pk))
        activation_link = reverse('activate', kwargs={'uidb64': uidb64, 'token': token})
        full_link = request.build_absolute_uri(activation_link)
        
        # Send activation email
        subject = "Fiók aktiválása"
        message = f"Hello {myuser.first_name} {myuser.last_name},\n\n" \
          "Köszönjük, hogy regisztráltál oldalunkon. Kérjük, kattints az alábbi linkre a fiókod aktiválásához:\n\n" \
          f"{full_link}\n\n"
        send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
        messages.success(request, "Sikeres létrehozás!! Ellenőrizze az e-mail fiókját a regisztráció aktiválásához.")
        
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
        myuser.save()
        messages.success(request, "Sikeres aktiválás, mostantól beléphetsz!!")
        return redirect('login')


def login(request):
    if request.user.is_authenticated:
        return redirect('disease_recognition')
    
    if request.method == 'POST':
        email = request.POST['email']
        pass1 = request.POST['pass1']
        
        user = django_auth(username=email, password=pass1)
        
        if user is not None:
            django_login(request, user)
            return redirect("disease_recognition")
        else:
            messages.error(request, "Nem megfelelő adatok!!")
            return redirect('login')
    
    return render(request, "authentication/login.html")


def signout(request):
    if not request.user.is_authenticated:
            return redirect('login')
    django_logout(request)
    messages.success(request, "Sikeres kijelentkezés!!")
    return redirect('login')


@login_required
def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, "authentication/profile.html", {"user": request.user})
