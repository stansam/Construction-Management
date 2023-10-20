from django.contrib import admin
from .models import Material, Project, MaterialAssignment

# Register your models here.
admin.site.register(Material)
admin.site.register(Project)
admin.site.register(MaterialAssignment)
