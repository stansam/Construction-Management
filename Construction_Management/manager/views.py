from django.shortcuts import render, redirect
from .models import Material, Project

from .forms import MaterialForm, MaterialUpdateForm, ProjectForm, MaterialAssignmentForm
from django.http import JsonResponse
from django.contrib import messages 

# Create your views here.


def index(request):
    material = Material.objects.all()
    project = Project.objects.all()
    return render(request, "manager/dashboard.html", {
        "materials" : material,
        "projects" : project
    })
def materials_available(request):
    return render(request, "manager/materials.html", {
        "materials": Material.objects.all()
    } )
def add_material(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            form.save()  # Save the material data to the database
            return redirect('materials_available')  # Redirect to the dashboard or another appropriate page after adding the material
    else:
        form = MaterialForm()
    
    return render(request, 'manager/add_materials.html', {
        'form': form
        })

def delete_material(request, material_id):
    try:
        material = Material.objects.get(pk=material_id)
        material.delete()
        return JsonResponse({"message": "Material deleted successfully."})
    except Material.DoesNotExist:
        return JsonResponse({"error": "Material not found."}, status=404)
    

def update_material_quantity(request):
    error_message = ""  
    success_message = ""
    if request.method == 'POST':
        form = MaterialUpdateForm(request.POST)
        if form.is_valid():
            material_name = form.cleaned_data['name']
            new_quantity = form.cleaned_data['quantity']

            try:
                material = Material.objects.get(name=material_name)
                material.quantity += new_quantity
                material.save()
                success_message = "Quantity updated successfully."
            except Material.DoesNotExist:
                error_message = "Material not found. Please check the name."

    else:
        form = MaterialUpdateForm()
        success_message = None
        error_message = None

    return render(request, 'manager/update_material.html', {
        'form': form,
        'success_message': success_message,
        'error_message': error_message,
    })

def all_projects(request):
    projects = Project.objects.all()
    return render(request, "manager/projects.html", {
        "projects": projects
    })

def add_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()  
            return redirect('projects')  

    else:
        form = ProjectForm()

    return render(request, 'manager/add_project.html', {'form': form})

def project_detail(request, project_id):
    project = Project.objects.get(pk=project_id)
    materials_assigned = project.materials.all()
    return render(request, "manager/project_detail.html", {
        'project': project,
        'materials_assigned': materials_assigned,

    })

def assign_materials(request, project_id):
    if request.method == 'POST':
        form = MaterialAssignmentForm(request.POST)
        if form.is_valid():
            material_name = form.cleaned_data['material_name']
            quantity_needed = form.cleaned_data['quantity_needed']
            
            try:
                material = Material.objects.get(name=material_name)
                if material.quantity >= quantity_needed:
                    material.quantity -= quantity_needed
                    material.save()
                    project = Project.objects.get(pk=project_id)
                    project.materials.add(material, through_defaults={'quantity_assigned': quantity_needed})
                    return redirect('project_detail', project_id=project_id)
                else:
                    messages.error(request, "Not enough material available.")
                    project = Project.objects.get(pk=project_id)
                    project.status = "Pending"
                    project.save()
                    return redirect('assign_materials', project_id=project_id)
                    # Handle the case where there isn't enough material
                    # You can set an error message and re-display the form
            except Material.DoesNotExist:
                messages.error(request, "Material not found.")
                # Handle the case where the material doesn't exist
                # You can set an error message and re-display the form
    else:
        form = MaterialAssignmentForm()
    
    return render(request, 'manager/assign_materials.html', {'form': form})

