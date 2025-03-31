from django.db import models

class PlantDisease(models.Model):
    name = models.CharField(max_length=255, unique=True)
    latin_name = models.CharField(max_length=255, unique=True)
    description = models.TextField() 
    causes = models.TextField() 
    treatment = models.TextField()
    severity = models.IntegerField(choices=[(1, 'Enyhe'), (2, 'Mérsékelt'), (3, 'Súlyos')])
    image = models.ImageField(upload_to='disease_images/', null=True, blank=True)


class Plant(models.Model):
    name = models.CharField(max_length=255, unique=True)
    latin_name = models.CharField(max_length=255, unique=True)
    family = models.CharField(max_length=255)
    genus = models.CharField(max_length=255)
    species = models.CharField(max_length=255)
    native_region = models.TextField()
    uses = models.TextField()
    distribution = models.TextField()
    image = models.ImageField(upload_to='plant_images/', null=True, blank=True)
