from django.urls import path
from . import views 

urlpatterns = [
    path("", views.index, name="index"),
    path("materials", views.materials_available, name="materials_available"),
    path("add_material", views.add_material, name="add_material")
    
]