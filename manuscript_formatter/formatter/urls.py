from django.urls import path
from . import views

urlpatterns = [
    path("",                views.home,              name="home"),
    path("format/",         views.format_file,       name="format_file"),
    path("format/custom/",  views.format_custom,     name="format_custom"),
    path("preview/",        views.preview_detection, name="preview_detection"),
]