from django.shortcuts import render
from keras.preprocessing import image
import numpy as np
import os
from keras.models import load_model

def model_view(request):
    # Betöltés a model.h5 fájlból
    model = load_model('aicore/model.h5')

    # Tesztelendő kép betöltése és előkészítése
    img_path = 'static/images/test.jpeg'  # Tesztelendő kép elérési útja
    img = image.load_img(img_path, target_size=(100, 100))  # Beolvasás és méretre alakítás
    img_array = image.img_to_array(img)  # Kép átalakítása tömbbé
    img_array = np.expand_dims(img_array, axis=0)  # Tömb dimenzióinak kiterjesztése

    # Kép tesztelése a modellen
    predictions = model.predict(img)
    train_dir = 'C:\\GroWise\\growise\\static\\images\\Disease\\train'
    class_directories = [d for d in os.listdir(train_dir) if os.path.isdir(os.path.join(train_dir,d))]
    labels = sorted(class_directories)
    context = {
        'predictions': predictions.tolist(),
        'labels': labels
    }
    return render(request, 'dashboard/model_result.html', context)