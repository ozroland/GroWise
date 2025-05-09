from django.db import models

class Disease(models.Model):
    common_name = models.CharField(max_length=255, unique=True)
    common_name_hu = models.CharField(max_length=255)
    pathogen = models.CharField(max_length=255)
    type = models.TextField()
    identification = models.TextField() 
    solutions = models.TextField()
    host = models.CharField(max_length=255)
    image = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['common_name']),
            models.Index(fields=['pathogen']),
        ]


class Plant(models.Model):
    botanical_name = models.CharField(max_length=255, unique=True)
    common_name = models.CharField(max_length=255, unique=True)
    family = models.CharField(max_length=255)
    genus = models.CharField(max_length=255)
    species = models.CharField(max_length=255)
    uses = models.TextField()
    distribution = models.TextField()
    image =  models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['common_name']),
        ]
