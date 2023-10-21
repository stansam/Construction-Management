from django.shortcuts import render, redirect, get_object_or_404
from .models import Material, Project, MaterialAssignment
from django.db.models import Sum, Count, F, Case, When
from .forms import MaterialForm, MaterialUpdateForm, ProjectForm, MaterialAssignmentForm
from django.http import JsonResponse
from django.contrib import messages 
from datetime import date
from django.db import transaction, models


# Tommorrow.
# add variables that calculate both individual ongoing and upcoming projects budget
# add a variable that calculates all upcoming projects budget
# show closest upcoming project in dashboard
# Continue enhancing the dashboard style


def index(request):
    material = Material.objects.all()
    project = Project.objects.all()
    less_materials = Material.objects.filter(quantity__lt=5)

    today = date.today()
    ongoing_projects = Project.objects.filter(start_date__lte=today, end_date__gte=today)
    total_budget = ongoing_projects.annotate(
        total_cost=Sum('materialassignment__cost')
    ).aggregate(total_budget=Sum('total_cost'))['total_budget'] or 0

    projects_lacking_materials = []
    for project_instance in project:
        lacking_materials = project_instance.get_lacking_materials()
        if lacking_materials:
            projects_lacking_materials.append({
                'project': project,
                'lacking_materials': lacking_materials,
            })
    return render(request, "manager/dashboard.html", {
        "materials" : material,
        "projects" : project,
        "ongoing_projects": ongoing_projects,
        "total_budget":total_budget,
        "projects_lacking_materials": projects_lacking_materials,
        "less_materials": less_materials
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
                update_projects_with_lacking_materials()
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
def update_project(request, project_id):
    project = Project.objects.get(pk=project_id)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'manager/update_project.html', {'form': form, 'project': project})

def project_detail(request, project_id):
    project = Project.objects.get(pk=project_id)
    materials_assigned = project.materials.all()
    total_budget = project.calculate_total_budget()
    return render(request, "manager/project_detail.html", {
        'project': project,
        'materials_assigned': materials_assigned,
        'total_budget': total_budget

    })



def assign_materials(request, project_id):
    
    project = Project.objects.get(pk=project_id)
    materials =  Material.objects.all()

    if request.method == 'POST':
        form = MaterialAssignmentForm(request.POST)
        if form.is_valid():
            material_name = form.cleaned_data['name']
            quantity_needed = form.cleaned_data['quantity_needed']

            try:
                material = Material.objects.get(name=material_name)                

                if material.quantity >= quantity_needed:
                    # Assign the same quantity as needed when enough material is available
                    quantity_assigned = quantity_needed
                else:
                    # If quantity_needed exceeds available quantity, set quantity_assigned to available quantity
                    quantity_assigned = material.quantity

                # Subtract the assigned quantity from material
                material.quantity -= quantity_assigned
                material.save()

                cost = material.unit_price * quantity_assigned

                

                # Create a material assignment for the project
                assignment = MaterialAssignment.objects.create(
                    name=material,
                    project=project,
                    quantity_needed=quantity_needed,
                    quantity_assigned=quantity_assigned,
                    cost=cost
                )

                

                # Set the status of the material based on the available quantity
                
                assignment.save()

                messages.success(request, "Material assigned successfully.")
                return redirect('assign_material', project_id=project_id)

            except Material.DoesNotExist:
                messages.error(request, "Material not found.")
                return redirect('assign_material', project_id=project_id)

    else:
        form = MaterialAssignmentForm()

    return render(request, 'manager/assign_material.html', {
        'form': form,
        'project': project,
        'materials': materials,
    })



def remove_assigned_material(request, project_id, material_assignment_id):
    
    material_assignment = get_object_or_404(MaterialAssignment, pk=material_assignment_id)

    # Calculate the amount being removed
    removed_quantity = material_assignment.quantity_assigned

    # Calculate the project with the lowest ID
    lowest_id_project = Project.objects.order_by('id').first()

    # Query for other projects with the same material and higher IDs
    other_projects = Project.objects.filter(
        materialassignment__name=material_assignment.name,
        id__gt=lowest_id_project.id
    )

    # Loop through other projects and update assigned quantities
    for other_project in other_projects:
        other_assignments = MaterialAssignment.objects.filter(
            project=other_project,
            name=material_assignment.name
        )

        for assignment in other_assignments:
            if removed_quantity > 0:
                # Calculate how much can be assigned to this project without exceeding quantity_needed
                remaining_quantity = min(removed_quantity, assignment.quantity_needed - assignment.quantity_assigned)
                assignment.quantity_assigned += remaining_quantity
                assignment.save()
                removed_quantity -= remaining_quantity

    # Increase the material quantity by the assigned quantity
    material = material_assignment.name
    material.quantity += removed_quantity
    material.save()

    # Delete the material assignment
    material_assignment.delete()

    return redirect('project_detail', project_id=project_id)


def remove_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        # Calculate assigned materials
        assigned_materials = MaterialAssignment.objects.filter(project=project)
        
        # Render confirmation page with assigned materials
        return render(request, 'manager/confirm_remove_project.html', {
            'project': project,
            'assigned_materials': assigned_materials,
        })

    return redirect('project_detail', project_id=project_id)

def confirm_project_removal(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        # Get assigned materials
        assigned_materials = MaterialAssignment.objects.filter(project=project)

        # Add assigned materials back to the overall quantity
        for assignment in assigned_materials:
            material = assignment.name
            material.quantity += assignment.quantity_assigned
            material.save()

        # Delete the project and its assignments
        project.delete()
        assigned_materials.delete()

        return redirect('project_detail')  # Redirect to the projects list page

    return redirect('project_detail', project_id=project_id)


def update_projects_with_lacking_materials():
    lacking_projects = Project.objects.filter(materialassignment__quantity_needed__gt=F('materialassignment__quantity_assigned'))
    sorted_projects = lacking_projects.order_by('id')

    for project in sorted_projects:
        lacking_materials = project.materialassignment_set.filter(quantity_assigned__lt=F('quantity_needed'))


        for assignment in lacking_materials:
            quantity_needed = assignment.quantity_needed
            quantity_assigned = assignment.quantity_assigned
            lacking_quantity = quantity_needed - quantity_assigned
            material = assignment.name 

            if material.quantity >= lacking_quantity:
                assignment.quantity_assigned = F('quantity_needed')
                material.quantity -= lacking_quantity
            else:
                assignment.quantity_assigned = F('quantity_assigned') + F('material__quantity')

            assignment.save()
            project.save()
            material.save()