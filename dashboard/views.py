from django.shortcuts import render, redirect


def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, "dashboard/profile.html", {"user": request.user})