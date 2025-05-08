from django.db import models

class Log(models.Model):
    LEVEL_CHOICES = [
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]

    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
