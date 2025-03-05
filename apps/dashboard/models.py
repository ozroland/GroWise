from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator

# Kép tábla
class Image(models.Model):
    image_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    image_filename = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    image_status = models.CharField(max_length=255, choices=[('Processing', 'Processing'), ('Processed', 'Processed')])

# Növény tábla
class Plant(models.Model):
    plant_id = models.AutoField(primary_key=True)
    plant_name = models.CharField(max_length=255)
    plant_type = models.CharField(max_length=255)
    image = models.ImageField(upload_to='plants')

# Betegségek tábla
class Disease(models.Model):
    disease_id = models.AutoField(primary_key=True)
    disease_name = models.CharField(max_length=255)
    description = models.TextField()
    symptoms = models.TextField()
    treatment_suggestions = models.TextField()
    image = models.ImageField(upload_to='diseases')

# Felismerések tábla
class Detection(models.Model):
    detection_id = models.AutoField(primary_key=True)
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    confidence_level = models.IntegerField(validators=[MaxValueValidator(100),MinValueValidator(1)])
    date = models.DateTimeField(auto_now_add=True)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
