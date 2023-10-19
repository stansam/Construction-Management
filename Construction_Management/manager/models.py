from django.db import models
from .constants import STATUS_CHOICES
from datetime import datetime


# Create your models here.
class Material(models.Model):
    name = models.CharField(max_length=100, unique=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.id}. {self.name}"

class Project(models.Model):
    title = models.CharField(max_length=100)
    location = models.CharField(max_length=64)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    materials = models.ManyToManyField(Material, through='MaterialUsage', related_name="materials_used")

    def __str__(self):
        return self.title



class MaterialUsage(models.Model):
    name = models.ForeignKey(Material, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
