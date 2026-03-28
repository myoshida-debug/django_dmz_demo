from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="open_index"),
    path("prompt/<str:filename>/", views.prompt_detail, name="open_prompt_detail"),

    path("", views.index, name="open_index"),
    path("<str:filename>/", views.prompt_detail, name="open_prompt_detail"),
    path("<str:filename>/delete/", views.prompt_delete, name="open_prompt_delete"),

]
