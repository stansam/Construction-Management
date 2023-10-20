from django.db import models
from .constants import STATUS_CHOICES
from datetime import date
from django.db.models import F, ExpressionWrapper, DecimalField


# Create your models here.
class Material(models.Model):
    name = models.CharField(max_length=100, unique=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.name}"

class Project(models.Model):
    title = models.CharField(max_length=100)
    location = models.CharField(max_length=64)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    materials = models.ManyToManyField(Material, through='MaterialAssignment', related_name="materials_used")
    def calculate_total_budget(self):
        total_budget = 0
        for assignment in self.materialassignment_set.all():
            total_budget += assignment.cost
        return total_budget


    def __str__(self):
        return self.title
    def get_status(self):
        today = date.today()
        if today < self.start_date:
            return 'Upcoming'
        elif self.start_date <= today <= self.end_date:
            return 'Ongoing'
        elif today > self.end_date:
            return 'Completed'
        return 'Unknown'  # Handle any other cases as needed

    def save(self, *args, **kwargs):
        self.status = self.get_status()
        super().save(*args, **kwargs)
    
    def get_lacking_materials(self):
        lacking_materials = self.materialassignment_set.exclude(quantity_assigned__gte=F('quantity_needed'))
        return lacking_materials



class MaterialAssignment(models.Model):
    name = models.ForeignKey(Material, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    quantity_needed = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_assigned = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    def save(self, *args, **kwargs):
        # Calculate the cost based on unit price and quantity assigned
        if self.name and self.quantity_assigned:
            self.cost = self.name.unit_price * self.quantity_assigned
        super(MaterialAssignment, self).save(*args, **kwargs)