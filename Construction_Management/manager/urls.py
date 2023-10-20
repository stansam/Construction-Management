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
    path("project_detail/<int:project_id>/", views.project_detail, name="project_detail"),
    path("update_project/<int:project_id>/", views.update_project, name="update_project"),
    path("assign_materials/<int:project_id>/", views.assign_materials, name="assign_material"),
    path("remove_project/<int:project_id>/", views.remove_project, name="remove_project"),
    path("remove_assigned_material/<int:project_id>/<int:material_assignment_id>/", views.remove_assigned_material, name="remove_assigned_material"),
    path("confirm_remove_project/<int:project_id>/", views.confirm_project_removal, name="confirm_remove_project" )
    
]