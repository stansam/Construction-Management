from django.urls import path
from . import views 

urlpatterns = [
    path("", views.index, name="index"),
    path("materials", views.materials_available, name="materials_available"),
    path('delete_material/<int:material_id>/', views.delete_material, name='delete_material'),
    path("update_material", views.update_material_quantity, name="update_material"),
    path("projects", views.all_projects, name="projects"),
    path("add_material", views.add_material, name="add_material"),
    path("add_project", views.add_project, name="add_project"),
    path("project_dtail/<int:project_id>/", views.project_detail, name="project_detail"),
    path("assign_materials/<int:project_id>/", views.assign_materials, name="assign_materials")
    
]