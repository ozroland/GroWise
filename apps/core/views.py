from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render, redirect

def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        full_message = f"Név: {name}\nEmail: {email}\nÜzenet:\n{message}"

        try:
            send_mail(
                subject="Kapcsolatfelvétel a weboldalról",
                message=full_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
            )
            messages.success(request, "Az üzenetet sikeresen elküldtük!")
        except:
            messages.error(request, "Hiba történt az üzenet küldésekor.")

        return redirect("home") 

    return render(request, "core/home.html")


def leaf_disease_info(request):
    return render(request, 'core/leaf_disease_info.html')


def plant_identifier_info(request):
    return render(request, 'core/plant_identifier_info.html')


def plant_database_info(request):
    return render(request, 'core/plant_database_info.html')
