from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from keras.preprocessing import image
import numpy as np
from keras.models import load_model

@api_view(['POST'])
#@permission_classes([IsAuthenticated])
def receive_image(request):
        # Kép ellenőrzése és mentése TODO
        
        # Kép elküldése a model-nek az azonosításhoz
        image_path = request.data['image']
        model = load_model('aitrain/model2.h5')
        img = image.load_img(image_path, target_size=(100, 100))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        predictions = model.predict(img_array)
        
        # Válasz elküldése
        return Response({'status': 'success', 'message': 'Image received, saved, and processed.', 'predictions': predictions.tolist()}, status=status.HTTP_201_CREATED)
