from django.db import models

class Plant(models.Model):
    name = models.CharField(max_length=100)
    plant_type = models.CharField(max_length=50)
    optimal_temperature_range = models.CharField(max_length=50)
    optimal_humidity_range = models.CharField(max_length=50)
    optimal_nutrient_levels = models.CharField(max_length=100)
    light_requirement = models.CharField(max_length=100)
    water_requirement = models.CharField(max_length=100)
    susceptibility_to_diseases = models.TextField()
    harvest_time = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
    
class OperatingData(models.Model):
    timestamp = models.DateTimeField()
    temperature = models.FloatField()
    humidity = models.FloatField()
    pH = models.FloatField()
    nutrient_levels = models.CharField(max_length=100)
    light_intensity = models.CharField(max_length=100)
    water_requirement = models.CharField(max_length=100)
    irrigation_amount = models.FloatField()
    nutrient_supply = models.CharField(max_length=100)
    plant_condition = models.CharField(max_length=50)
    harvest_quantity = models.FloatField()

    def __str__(self):
        return str(self.timestamp)