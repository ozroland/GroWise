from django.shortcuts import render, get_object_or_404
from .models import Disease, Plant
from django.contrib.auth.decorators import login_required


@login_required
def disease_list(request):
    disease = Disease.objects.all()
    return render(request, 'plant/disease_list.html', {'disease': disease})


@login_required
def disease_detail(request, disease_id):
    disease = get_object_or_404(Disease, id=disease_id)
    return render(request, 'plant/disease_detail.html', {'disease': disease})


@login_required
def plant_list(request):
    plant = Plant.objects.all()
    return render(request, 'plant/plant_list.html', {'plant': plant})


@login_required
def plant_detail(request, plant_id):
    plant = get_object_or_404(Plant, id=plant_id)
    return render(request, 'plant/plant_detail.html', {'plant': plant})
