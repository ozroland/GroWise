import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Image, Result
from django.conf import settings
from django.shortcuts import redirect
from PIL import Image as PILImage
from django.core.files.storage import default_storage
import torch
from django.contrib import messages
from apps.core.model_loader import model, device, transform, disease_labels_hu, to_device
import logging

logger = logging.getLogger(__name__)


@login_required
def recognition(request, image_type='disease'):
    try:
        user_images = Image.objects.filter(user=request.user, image_type=image_type).order_by('-created_at')

        if request.method == 'POST' and request.FILES.getlist('images'):
            images = request.FILES.getlist('images')

            for image in images:
                new_image = Image(
                    user=request.user,
                    image=image,
                    image_type=image_type
                )
                new_image.save()

            return redirect('recognition', image_type=image_type)

        template_name = f"recognition/{image_type.lower()}_recognition.html"
        return render(request, template_name, {"user_images": user_images})
    
    except Exception as e:
        logger.error(f"Hiba történt a képek feltöltése közben: {str(e)}")
        messages.error(request, "Hiba történt a képek feltöltése közben!")
        return redirect('recognition', image_type='disease')


@login_required
def evaluate_disease(request):
    try:
        if request.method == "POST":
            selected_image_ids = request.POST.getlist('selected_images')
            if not selected_image_ids:
                return redirect('recognition', image_type='disease')

            images = Image.objects.filter(id__in=selected_image_ids, image_type='disease')

            for image in images:

                if image.image_status == 'Feldolgozva':
                    continue
                
                img_path = image.image.path
                img = PILImage.open(img_path).convert('RGB')
                img_tensor = transform(img)
                xb = to_device(img_tensor.unsqueeze(0), device)

                with torch.no_grad():
                    outputs = model(xb)
                    _, predicted = torch.max(outputs, dim=1)
                    predicted_class = predicted[0].item()
                    confidence_score = torch.softmax(outputs, dim=1)[0][predicted_class].item()

                label_keys = list(disease_labels_hu.keys())
                predicted_class_name = disease_labels_hu[label_keys[predicted_class]]

                confidence_percent = round(confidence_score * 100, 2)

                image.image_status = 'Feldolgozva'
                image.save()

                recognition_result = Result(
                    user=image.user,
                    image=image,
                    detected_disease=predicted_class_name,
                    disease_confidence_level=confidence_percent
                )
                recognition_result.save()

            logger.info(f"Disease recognition completed for user {request.user.email}.")
        return redirect('recognition', image_type='disease')
    
    except Exception as e:
        logger.error(f"Hiba történt a betegség felismerés közben: {str(e)}")
        messages.error(request, "Hiba történt a betegség felismerés közben!")
        return redirect('recognition', image_type='disease')


@login_required
def evaluate_plant(request):
    try:
        if request.method == "POST":
            selected_image_ids = request.POST.getlist('selected_images')
            if not selected_image_ids:
                return redirect('recognition', image_type='plant')

            images = Image.objects.filter(id__in=selected_image_ids, image_type='plant')

            for image in images:
                img_path = image.image.path

                url = f"https://my-api.plantnet.org/v2/identify/all"
                files = {"images": open(img_path, "rb")}
                params = {
                    "api-key": settings.PLANTNET_API_KEY,
                    "lang": "hu",
                    "include-related-images": "false",
                    "nb-results": 1
                }

                response = requests.post(url, files=files, params=params)
                response_data = response.json()

                if "results" in response_data and response_data["results"]:
                    result = response_data["results"][0]
                    predicted_plant = result["species"].get("commonNames")[0]
                    confidence = result["score"]
                    confidence_percent = round(confidence * 100, 2)

                    image.image_status = 'Feldolgozva'
                    image.save()

                    recognition_result = Result(
                        user=image.user,
                        image=image,
                        detected_plant=predicted_plant,
                        plant_confidence_level=confidence_percent
                    )
                    recognition_result.save()

            logger.info(f"Plant recognition completed for user {request.user.email}.")
            return redirect('recognition', image_type='plant')
        
    except Exception as e:
        logger.error(f"Hiba történt a növény felismerés közben: {str(e)}")
        messages.error(request, "Hiba történt a növény felismerés közben!")
        return redirect('recognition', image_type='plant')
    
    return redirect('recognition', image_type='plant')


@login_required
def delete_images(request, image_type='disease'):
    try:
        if request.method == "POST":
            selected_image_ids = request.POST.getlist('selected_images')
            image_type = request.POST.get('image_type')

            if selected_image_ids:
                images = Image.objects.filter(id__in=selected_image_ids)

                for image in images:
                    if image.image:
                        file_path = image.image.path
                        if default_storage.exists(file_path):
                            default_storage.delete(file_path)

                    Result.objects.filter(image=image).delete()

                    image.delete()

            logger.info(f"Images deleted by user {request.user.email}.")
        return redirect('recognition', image_type=image_type)

    except Exception as e:
        logger.error(f"Hiba történt a képek törlése közben: {str(e)}")
        messages.error(request, "Hiba történt a képek törlése közben!")
        return redirect('recognition', image_type=image_type)
