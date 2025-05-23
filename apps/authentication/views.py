from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth import authenticate as django_auth, login as django_login, logout as django_logout
from apps.recognition.models import Image, Result
from . tokens import generate_token
from .models import User
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.contrib.auth.views import PasswordResetCompleteView,PasswordResetDoneView
import os
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


def home(request):
    if request.user.is_authenticated:
        return redirect('recognition', image_type='disease')
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
            logger.warning(f"Regisztrációs próbálkozás e-mail cím foglalás miatt: {email}")
            messages.error(request, "Foglalt e-mail cím!!")
            return redirect('signup')
        
        if pass1 != pass2:
            logger.warning(f"Jelszó nem egyezés: {email}")
            messages.error(request, "A jelszavak nem egyeztek meg!!")
            return redirect('signup')
        
        try:
            validate_password(pass1)
        except ValidationError as e:
            for error in e:
                logger.warning(f"Jelszó hiba ({email}): {error}")
                messages.error(request, error)
            return redirect('signup')
        try:
            myuser = User.objects.create_user(email, email, pass1)
            myuser.first_name = fname
            myuser.last_name = lname
            myuser.is_active = False
            myuser.save()

            token = generate_token.make_token(myuser)
            uidb64 = urlsafe_base64_encode(force_bytes(myuser.pk))
            activation_link = reverse('activate', kwargs={'uidb64': uidb64, 'token': token})
            full_link = request.build_absolute_uri(activation_link)
            
            subject = "Fiók aktiválása"
            message = f"Hello {myuser.first_name} {myuser.last_name},\n\n" \
            "Köszönjük, hogy regisztráltál oldalunkon. Kérjük, kattints az alábbi linkre a fiókod aktiválásához:\n\n" \
            f"{full_link}\n\n"
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
            messages.success(request, "Sikeres létrehozás!! Ellenőrizze az e-mail fiókját a regisztráció aktiválásához.")
            logger.info(f"Új felhasználó regisztrálva: {email}")
        except Exception as e:
            logger.error(f"Regisztrációs hiba ({email}): {e}")
            messages.error(request, "Valami hiba történt a regisztráció során.")
        
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
    else:
        messages.error(request, "Érvénytelen aktiválási link!")
        return redirect('login')


def login(request):
    if request.user.is_authenticated:
        return redirect('recognition', image_type='disease')
    
    if request.method == 'POST':
        email = request.POST['email']
        pass1 = request.POST['pass1']
        
        user = django_auth(username=email, password=pass1)
        
        if user is not None:
            django_login(request, user)
            logger.info(f"Felhasználó sikeresen bejelentkezett: {email}")
            return redirect('recognition', image_type='disease')
        else:
            logger.warning(f"Sikertelen bejelentkezés próbálkozás: {email}")
            messages.error(request, "Nem megfelelő adatok!!")
            return redirect('login')
    
    return render(request, "authentication/login.html")


@login_required
def signout(request):
    django_logout(request)
    messages.success(request, "Sikeres kijelentkezés!!")
    return redirect('login')


@login_required
def profile(request):
    user = request.user
    total_disease_recognitions = Image.objects.filter(user=user, image_type='disease', image_status='Feldolgozva').count()
    total_plant_recognitions = Image.objects.filter(user=user, image_type='plant', image_status='Feldolgozva').count()
    recent_results = Result.objects.filter(user=user).order_by('-created_at')[:10]

    logger.info(f"Felhasználói profil betöltve: {user.email}, Daganat felismerések: {total_disease_recognitions}, Növény felismerések: {total_plant_recognitions}")
    
    context = {
        "user": user,
        "total_disease_recognitions": total_disease_recognitions,
        "total_plant_recognitions": total_plant_recognitions,
        "recent_results": recent_results,
    }
    return render(request, "authentication/profile.html", context)


def download_terms_pdf(request):
    pdf_path = os.path.join("static", "docs", "terms_and_conditions.pdf")
    return FileResponse(open(pdf_path, "rb"), content_type="application/pdf", as_attachment=True, filename="ASZF_GroWise.pdf")


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "A jelszavad sikeresen módosítva lett.")
            return redirect('profile')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'authentication/profile.html', {'form': form})


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    def get(self, request, *args, **kwargs):
        messages.success(request, "A jelszavad sikeresen megváltozott! Most már bejelentkezhetsz.")
        return redirect('login')    


class CustomPasswordResetDoneView(PasswordResetDoneView):
    def get(self, request, *args, **kwargs):
        messages.success(request, "Elküldtük az email címedre a jelszó-visszaállítási linket!")
        return redirect('login')
