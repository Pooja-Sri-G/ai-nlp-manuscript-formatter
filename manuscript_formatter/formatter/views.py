
import os
import json

from django.shortcuts import render
from django.http import FileResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .formatter_engine import format_document, TEMPLATES


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _save_upload(file) -> str:
    """Save an uploaded file to MEDIA_ROOT and return its path."""
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    upload_path = os.path.join(settings.MEDIA_ROOT, file.name)
    with open(upload_path, "wb+") as dest:
        for chunk in file.chunks():
            dest.write(chunk)
    return upload_path


def _output_path(filename: str, prefix: str = "formatted_") -> str:
    return os.path.join(settings.MEDIA_ROOT, prefix + filename)


# ──────────────────────────────────────────────────────────────────────────────
# Views
# ──────────────────────────────────────────────────────────────────────────────

def home(request):
    """Render the main upload page with template options."""
    templates = list(TEMPLATES.keys())
    return render(request, "index.html", {"templates": templates})


def format_file(request):
    """
    POST: Upload a .docx + choose a built-in format template.
    Returns the formatted .docx as a download.
    """
    if request.method != "POST":
        return render(request, "index.html", {"templates": list(TEMPLATES.keys())})

    template_name = request.POST.get("template", "ieee")
    if template_name == "custom":
        from django.shortcuts import redirect
        return redirect("format_custom")

    manuscript = request.FILES.get("manuscript")
    if not manuscript:
        return render(request, "index.html", {
            "error": "No file uploaded.",
            "templates": list(TEMPLATES.keys()),
        })

    if template_name not in TEMPLATES:
        template_name = "ieee"

    upload_path = _save_upload(manuscript)
    output_path = _output_path(manuscript.name)

    try:
        report = format_document(upload_path, output_path, template_name=template_name)
    except Exception as e:
        return render(request, "index.html", {
            "error": f"Formatting failed: {e}",
            "templates": list(TEMPLATES.keys()),
        })

    response = FileResponse(open(output_path, "rb"), as_attachment=True,
                            filename=f"formatted_{manuscript.name}")
    return response


def format_custom(request):
    if request.method != "POST":
        return render(request, "custom_format.html")

    manuscript = request.FILES.get("manuscript")
    custom_json = request.POST.get("custom_template", "{}")

    if not manuscript:
        return render(request, "custom_format.html", {"error": "No file uploaded."})

    try:
        custom_template = json.loads(custom_json)
    except json.JSONDecodeError as e:
        return render(request, "custom_format.html", {"error": f"Invalid JSON: {e}"})

    upload_path = _save_upload(manuscript)
    output_path = _output_path(manuscript.name, prefix="custom_formatted_")

    try:
        report = format_document(
            upload_path, output_path,
            template_name="custom",
            custom_template=custom_template,
        )
    except Exception as e:
        return render(request, "custom_format.html", {"error": f"Formatting failed: {e}"})

    response = FileResponse(open(output_path, "rb"), as_attachment=True,
                            filename=f"custom_formatted_{manuscript.name}")
    return response


@csrf_exempt
def preview_detection(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    manuscript = request.FILES.get("manuscript")
    if not manuscript:
        return JsonResponse({"error": "No file uploaded."}, status=400)

    template_name = request.POST.get("template", "ieee")
    upload_path = _save_upload(manuscript)
    output_path = _output_path(manuscript.name, prefix="preview_")

    try:
        report = format_document(upload_path, output_path, template_name=template_name)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse(report)