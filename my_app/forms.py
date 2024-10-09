from django import forms
from .models import FormConfig

def create_dynamic_form(form_id):
    class DynamicForm(forms.Form):
        form_config = FormConfig.objects.get(id=form_id)
        config = form_config.fields 
        field_data = config.get('fields', [])

        for field in field_data:
            field_type = field['type']
            is_required = field.get('required', True)  # Default to True if 'required' key is not present

            if field_type == 'text':
                locals()[field['name']] = forms.CharField(label=field['label'], required=is_required)
            elif field_type == 'email':
                locals()[field['name']] = forms.EmailField(label=field['label'], required=is_required)
            elif field_type == 'textarea':
                locals()[field['name']] = forms.CharField(widget=forms.Textarea, label=field['label'], required=is_required)
            elif field_type == 'number':
                locals()[field['name']] = forms.IntegerField(label=field['label'], required=is_required)
            elif field_type == 'image':
                locals()[field['name']] = forms.ImageField(label=field['label'], required=is_required)
            elif field_type == 'select':  # Handle choice field
                choices = field.get('choices', [])  # Expecting a 'choices' key in the field definition
                choice_list = [(choice['value'], choice['label']) for choice in choices]
                locals()[field['name']] = forms.ChoiceField(choices=choice_list, label=field['label'], required=is_required)
            # You can add more field types here

    return DynamicForm