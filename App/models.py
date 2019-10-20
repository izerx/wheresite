from django.db import models

class Results(models.Model):
    url = models.CharField(max_length=300, blank=True, null=True)
    save_url = models.CharField(max_length=300, blank=True, null=True)
    points = models.CharField(max_length=10000, blank=True, null=True) 
