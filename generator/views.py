import os
import subprocess
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ProjectSpecificationSerializer

class GenerateProjectView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ProjectSpecificationSerializer(data=request.data)
        if serializer.is_valid():
            specification = serializer.validated_data
            try:
                # Create the Django project
                base_path = create_django_project(specification)
                project_name = specification["project_name"]

                # Path to the manage.py file
                manage_py_path = os.path.join(base_path, project_name, "manage.py")

                # Run migrations
                subprocess.run(
                    ["python", manage_py_path, "migrate"],
                    cwd=os.path.join(base_path, project_name),
                    check=True,
                )

                # Start the server on an available port
                port = find_available_port()
                server_process = subprocess.Popen(
                    ["python", manage_py_path, "runserver", f"127.0.0.1:{port}"],
                    cwd=os.path.join(base_path, project_name),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                # Save the process ID for later management (optional)
                with open(os.path.join(base_path, "server.pid"), "w") as f:
                    f.write(str(server_process.pid))

                # Return the link to the user
                link = f"http://127.0.0.1:{port}"
                return Response(
                    {"message": f"Project created and running at {link}", "link": link},
                    status=status.HTTP_201_CREATED,
                )
            except subprocess.CalledProcessError as e:
                return Response(
                    {"error": f"Subprocess error: {e.stderr}"}, status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def find_available_port():
    import socket
    from contextlib import closing

    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def create_django_project(specification):
    project_name = specification["project_name"]
    app_name = specification["app_name"]

    try:
        models_spec = json.loads(specification["models_spec"])
        endpoints_spec = json.loads(specification["endpoints_spec"])
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON provided: {e}")

    # Base path for the generated project
    base_path = os.path.join("generated_projects", project_name)
    os.makedirs(base_path, exist_ok=True)

    # Create the Django project
    subprocess.run(
        ["django-admin", "startproject", project_name, base_path], check=True
    )

    # Path to the manage.py file
    manage_py_path = os.path.join(base_path, project_name, "manage.py")

    # Create the app inside the project
    subprocess.run(
        ["python", manage_py_path, "startapp", app_name],
        cwd=os.path.join(base_path, project_name),
        check=True,
    )

    # Path to the app directory
    app_path = os.path.join(base_path, project_name, app_name)
    os.makedirs(app_path, exist_ok=True)

    # Generate app files
    generate_app_files(app_path, models_spec, endpoints_spec, base_path, project_name, app_name)

    return base_path


def generate_app_files(app_path, models_spec, endpoints_spec, base_path, project_name, app_name):
    # Generate models.py
    models_code = generate_models_code(models_spec)
    with open(os.path.join(app_path, "models.py"), "w") as f:
        f.write(models_code)

    # Generate views.py and urls.py
    views_code, urls_code = generate_views_and_urls_code(endpoints_spec)
    with open(os.path.join(app_path, "views.py"), "w") as f:
        f.write(views_code)
    with open(os.path.join(app_path, "urls.py"), "w") as f:
        f.write(urls_code)

    # Generate admin.py
    admin_code = generate_admin_code(models_spec)
    with open(os.path.join(app_path, "admin.py"), "w") as f:
        f.write(admin_code)

    # Generate forms.py
    forms_code = generate_forms_code(models_spec)
    with open(os.path.join(app_path, "forms.py"), "w") as f:
        f.write(forms_code)

    # Add the app to INSTALLED_APPS
    add_app_to_installed_apps(base_path, project_name, app_name)

    # Generate apps.py
    apps_code = generate_apps_code(app_name)
    with open(os.path.join(app_path, "apps.py"), "w") as f:
        f.write(apps_code)

    # Generate project-level urls.py
    project_urls_path = os.path.join(base_path, project_name, "urls.py")
    project_urls_code = generate_urls_code(app_name)
    with open(project_urls_path, "w") as f:
        f.write(project_urls_code)

    # Generate tests.py
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
    class_name = "".join(part.capitalize() for part in sanitized_app_name.split("."))
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