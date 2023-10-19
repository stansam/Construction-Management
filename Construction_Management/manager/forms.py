from django import forms
from .models import Material, Project



class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['name', 'quantity', 'unit_price']

        def clean(self):
            cleaned_data = super().clean()
            material_name = cleaned_data.get('name')
            quantity = cleaned_data.get('quantity')

            # Check if a material with the same name already exists in the database
            existing_material = Material.objects.filter(name=material_name).first()

            if existing_material.exists():
                # If the material exists, update the form's quantity with the new value
                cleaned_data['quantity'] = existing_material.quantity + quantity

            return cleaned_data
        
class MaterialUpdateForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    quantity = forms.IntegerField(required=True)

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["title", "location", "start_date", "end_date", "status"]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
        
class MaterialAssignmentForm(forms.Form):
    material_name = forms.CharField(label='Material Name', max_length=100)
    quantity_needed = forms.IntegerField(label='Quantity Needed')

