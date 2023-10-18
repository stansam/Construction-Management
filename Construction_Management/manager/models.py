from django.db import models

# Create your models here.
class Material(models.Model):
    name = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.id}. {self.name}"

class Project(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.id}. {self.name}"

class MaterialUsage(models.Model):
    name = models.ForeignKey(Material, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
