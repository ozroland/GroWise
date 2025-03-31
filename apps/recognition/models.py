from django.db import models
from django.contrib.auth import get_user_model


class Image(models.Model):
    IMAGE_STATUS_CHOICES = [
        ('Uploaded', 'Uploaded'),
        ('Processed', 'Processed'),
        ('Failed', 'Failed'),
    ]

    IMAGE_TYPE_CHOICES = [
        ('Disease', 'Disease'),
        ('Plant', 'Plant'),
    ]

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    image = models.ImageField(upload_to='user_uploads/', null=True, blank=True)
    image_status = models.CharField(max_length=20, choices=IMAGE_STATUS_CHOICES, default='Uploaded')
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True) 


class RecognitionResult(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    detected_plant = models.CharField(max_length=50)
    detected_disease = models.CharField(max_length=50)
    plant_confidence_level = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    disease_confidence_level = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
