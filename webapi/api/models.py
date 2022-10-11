from django.db import models

# Create your models here.
class Violator(models.Model):
    
    image = models.CharField(max_length=200)
    missing_ppe = models.CharField(max_length=250)
    timestamp = models.DateTimeField(auto_now_add=True)