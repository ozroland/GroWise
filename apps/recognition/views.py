import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Image, RecognitionResult
from django.contrib import messages
import os
import numpy as np
import tensorflow as tf
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from PIL import Image as PILImage
from django.core.files.storage import default_storage


@login_required
def disease_recognition(request):
    user_images = Image.objects.filter(user=request.user, image_type='Disease').order_by('-created_at')

    if request.method == 'POST' and request.FILES.getlist('images'):
        images = request.FILES.getlist('images')

        for image in images:
            new_image = Image(
                user=request.user,
                image=image,
                image_type="Disease"
            )
            new_image.save()

        return redirect('disease_recognition')

    return render(request, "recognition/disease_recognition.html", {"user_images": user_images})


@login_required
def plant_recognition(request):
    user_images = Image.objects.filter(user=request.user, image_type='Plant').order_by('-created_at')

    if request.method == 'POST' and request.FILES.getlist('images'):
        images = request.FILES.getlist('images')

        for image in images:
            new_image = Image(
                user=request.user,
                image=image,
                image_type="Plant"
            )
            new_image.save()

        return redirect('plant_recognition')

    return render(request, "recognition/plant_recognition.html", {"user_images": user_images})


@login_required
def evaluate_disease(request):
    model_path = os.path.join(settings.BASE_DIR, 'tomato_leaf_disease_model.keras')

    try:
        model = tf.keras.models.load_model(model_path)
        class_names = ['Bacterial spot','Early blight','Late blight','Leaf Mold','Septoria leaf spot','Spider mites','Target Spot','Yellow Leaf Curl Virus','Mosaic virus','Healthy']
    except Exception as e:
        messages.error(request, f"Hiba a modell betöltése során: {str(e)}")
        return redirect('dashboard')

    if request.method == "POST":
        selected_image_ids = request.POST.getlist('selected_images')
        if not selected_image_ids:
            return redirect('disease_recognition')

        images = Image.objects.filter(id__in=selected_image_ids, image_type='Disease')
        
        for image in images:
            try:
                img_path = image.image.path
                img = PILImage.open(img_path)
                img = img.resize((256, 256))  
                img_array = np.array(img) / 255.0
                img_array = np.expand_dims(img_array, axis=0)
                
                prediction = model.predict(img_array)
                predicted_class = np.argmax(prediction, axis=1)[0]
                predicted_class_name = class_names[predicted_class]
                confidence = round(float(prediction[0][predicted_class] * 100), 2)

                image.image_status = 'Processed'
                image.save()

                recognition_result = RecognitionResult(
                    user=image.user,
                    image=image,
                    detected_disease=predicted_class_name,
                    disease_confidence_level=confidence
                )
                recognition_result.save()

            except Exception as e:
                messages.error(request, f"Hiba a kép kiértékelése során: {str(e)}")

        return redirect('disease_recognition')
    
    return redirect('disease_recognition')


@login_required
def evaluate_plant(request):
    if request.method == "POST":
        selected_image_ids = request.POST.getlist('selected_images')
        if not selected_image_ids:
            return redirect('plant_recognition')

        images = Image.objects.filter(id__in=selected_image_ids, image_type='Plant')

        for image in images:
            try:
                img_path = image.image.path
                
                url = f"https://my-api.plantnet.org/v2/identify/all"
                files = {"images": open(img_path, "rb")}
                params = {
                    "api-key": settings.PLANTNET_API_KEY,
                    "lang": "hu",
                    "include-related-images": "false",
                    "nb-results": 3
                }

                response = requests.post(url, files=files, params=params)
                print("Status Code:", response.status_code)
                response_data = response.json()

                if "results" in response_data and response_data["results"]:
                    best_match = response_data["results"][0]
                    predicted_species = best_match["species"]["scientificName"]
                    confidence = best_match["score"]
                    confidence_percent = round(confidence * 100, 2)
                    
                    image.image_status = 'Processed'
                    image.save()

                    recognition_result = RecognitionResult(
                        user=image.user,
                        image=image,
                        detected_plant=predicted_species,
                        plant_confidence_level=confidence_percent
                    )
                    recognition_result.save()

                    messages.success(request, f"Növény felismerve: {predicted_species} ({confidence*100:.2f}%)")

                else:
                    messages.warning(request, "Nem sikerült azonosítani a növényt.")

            except Exception as e:
                messages.error(request, f"Hiba történt: {str(e)}")

        return redirect('plant_recognition')

    return redirect('plant_recognition')


@login_required
def delete_images(request):
    if request.method == "POST":
        selected_image_ids = request.POST.getlist('selected_images')

        if selected_image_ids:
            images = Image.objects.filter(id__in=selected_image_ids)

            for image in images:
                if image.image:
                    file_path = image.image.path
                    print(f"Törlendő fájl: {file_path}")
                    if default_storage.exists(file_path):
                        default_storage.delete(file_path)

                RecognitionResult.objects.filter(image=image).delete()

                image.delete()

    referer = request.META.get('HTTP_REFERER', '')
    if 'disease' in referer:
        return redirect('disease_recognition')
    elif 'plant' in referer:
        return redirect('plant_recognition')

    return redirect('disease_recognition')
