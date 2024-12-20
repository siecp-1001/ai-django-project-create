from django.shortcuts import render
from .forms import ProjectSpecificationForm
from .utils import create_django_project

def generate_project(request):
    if request.method == "POST":
        form = ProjectSpecificationForm(request.POST)
        if form.is_valid():
            spec = {
                "project_name": form.cleaned_data["project_name"],
                "app_name": form.cleaned_data["app_name"],
                "models_spec": form.cleaned_data["models_spec"],
                "endpoints_spec": form.cleaned_data["endpoints_spec"],
            }
            project_path = create_django_project(spec)
            return render(request, "generator/success.html", {"project_path": project_path})
    else:
        form = ProjectSpecificationForm()

    return render(request, "generator/generate.html", {"form": form})
