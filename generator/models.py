from django.db import models

class ProjectSpecification(models.Model):
    project_name = models.CharField(max_length=100)
    app_name = models.CharField(max_length=100)
    models_spec = models.TextField(help_text="JSON format for models and fields.")
    endpoints_spec = models.TextField(help_text="JSON format for endpoints.")
    created_at = models.DateTimeField(auto_now_add=True)
