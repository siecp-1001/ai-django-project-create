from django import forms

class ProjectSpecificationForm(forms.Form):
    project_name = forms.CharField(max_length=100)
    app_name = forms.CharField(max_length=100)
    models_spec = forms.CharField(widget=forms.Textarea, help_text="JSON format for models.")
    endpoints_spec = forms.CharField(widget=forms.Textarea, help_text="JSON format for endpoints.")
