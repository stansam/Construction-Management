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
        fields = ["title", "location", "start_date", "end_date"]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
        
class MaterialAssignmentForm(forms.Form):
    name = forms.ModelChoiceField(
        queryset=Material.objects.all(),
        empty_label=None,  # If you don't want an empty label
        to_field_name='name',  # Set this to the field name you want to display in the dropdown
        label='Material Name'
    )
    quantity_needed = forms.DecimalField(min_value=0, max_value=9999999, decimal_places=2)
    

    
    
