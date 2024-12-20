import os
import subprocess
import json

def create_django_project(specification):
    project_name = specification["project_name"]
    app_name = specification["app_name"]

    try:
        models_spec = json.loads(specification["models_spec"])
        endpoints_spec = json.loads(specification["endpoints_spec"])
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON provided: {e}")

    base_path = f"generated_projects/{project_name}"
    os.makedirs(base_path, exist_ok=True)

    subprocess.run(["django-admin", "startproject", project_name, base_path])

    manage_py_path = os.path.join(base_path, project_name, "manage.py")
    subprocess.run(["python", manage_py_path, "startapp", app_name], cwd=os.path.join(base_path, project_name))

    app_path = os.path.join(base_path, project_name, app_name)
    os.makedirs(app_path, exist_ok=True)

    generate_app_files(app_path, models_spec, endpoints_spec, base_path, project_name, app_name)

    return base_path

def generate_app_files(app_path, models_spec, endpoints_spec, base_path, project_name, app_name):
    models_code = generate_models_code(models_spec)
    with open(os.path.join(app_path, "models.py"), "w") as f:
        f.write(models_code)

    views_code, urls_code = generate_views_and_urls_code(endpoints_spec)
    with open(os.path.join(app_path, "views.py"), "w") as f:
        f.write(views_code)
    with open(os.path.join(app_path, "urls.py"), "w") as f:
        f.write(urls_code)

    admin_code = generate_admin_code(models_spec)
    with open(os.path.join(app_path, "admin.py"), "w") as f:
        f.write(admin_code)

    forms_code = generate_forms_code(models_spec)
    with open(os.path.join(app_path, "forms.py"), "w") as f:
        f.write(forms_code)

    add_app_to_installed_apps(base_path, project_name, app_name)
    
    apps_code = generate_apps_code(app_path.split("/")[-1]) 
    with open(os.path.join(app_path, "apps.py"), "w") as f:
        f.write(apps_code)

    project_urls_path = os.path.join(base_path, project_name, "urls.py")
    project_urls_code = generate_urls_code(app_path.split("/")[-1])
    with open(project_urls_path, "w") as f:
        f.write(project_urls_code)

    tests_code = generate_tests_code()
    with open(os.path.join(app_path, "tests.py"), "w") as f:
        f.write(tests_code)

def add_app_to_installed_apps(base_path, project_name, app_name):
    project_settings_path = os.path.join(base_path, project_name, "settings.py")

    with open(project_settings_path, "r") as f:
        settings_code = f.readlines()

    installed_apps_line = None
    for i, line in enumerate(settings_code):
        if line.startswith("INSTALLED_APPS"):
            installed_apps_line = i
            break

    if installed_apps_line is not None:
        installed_apps_code = settings_code[installed_apps_line]
        if not installed_apps_code.endswith(",\n"):
            installed_apps_code = installed_apps_code.strip() + ",\n"

        
        installed_apps_code = installed_apps_code.rstrip(",\n") + f" '{app_name}',\n"

        settings_code[installed_apps_line] = installed_apps_code

    with open(project_settings_path, "w") as f:
        f.writelines(settings_code)

def generate_models_code(models_spec):
    models_code = "from django.db import models\n\n"
    for model_name, fields in models_spec.items():
        models_code += f"class {model_name}(models.Model):\n"
        for field_name, field_type in fields.items():
            models_code += f"    {field_name} = models.{field_type}\n"
        models_code += "\n"
    return models_code

def generate_views_and_urls_code(endpoints_spec):
    views_code = "from django.http import JsonResponse\n\n"
    urls_code = "from django.urls import path\nfrom . import views\n\nurlpatterns = [\n"

    for endpoint, details in endpoints_spec.items():
        views_code += f"def {endpoint}(request):\n    return JsonResponse({{'message': 'Hello from {endpoint}'}})\n\n"
        urls_code += f"    path('{details['path']}/', views.{endpoint}, name='{endpoint}'),\n"

    urls_code += "]\n"
    return views_code, urls_code

def generate_admin_code(models_spec):
    admin_code = "from django.contrib import admin\nfrom .models import *\n\n"
    for model_name in models_spec.keys():
        admin_code += f"admin.site.register({model_name})\n"
    return admin_code

def generate_forms_code(models_spec):
    forms_code = "from django import forms\nfrom .models import *\n\n"
    for model_name in models_spec.keys():
        forms_code += f"class {model_name}Form(forms.ModelForm):\n"
        forms_code += f"    class Meta:\n"
        forms_code += f"        model = {model_name}\n"
        forms_code += f"        fields = '__all__'\n\n"
    return forms_code

def generate_apps_code(app_name):
    sanitized_app_name = app_name.replace("\\", ".").replace("/", ".")
    class_name = ''.join(part.capitalize() for part in sanitized_app_name.split("."))
    return f"""from django.apps import AppConfig\n\n\nclass {class_name}Config(AppConfig):\n    default_auto_field = 'django.db.models.BigAutoField'\n    name = '{sanitized_app_name}'\n"""

def generate_tests_code():
    return """from django.test import TestCase\n\n\nclass BasicTests(TestCase):\n    def test_basic_functionality(self):\n        self.assertEqual(1 + 1, 2)\n"""

def generate_urls_code(app_name):
    sanitized_app_name = app_name.split("/")[-1].split("\\")[-1]
    return f"""from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('{sanitized_app_name}.urls')),
]
"""
if __name__ == "___MAIN__":
    pass
