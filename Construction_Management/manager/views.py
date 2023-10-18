from django.shortcuts import render, redirect
from .models import Material, Project

from .forms import MaterialForm
from django.http import HttpResponseRedirect

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