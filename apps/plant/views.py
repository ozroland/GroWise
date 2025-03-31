from django.shortcuts import render, redirect


def disease_list(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, "authentication/profile.html", {"user": request.user})


def plant_list(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, "authentication/profile.html", {"user": request.user})
