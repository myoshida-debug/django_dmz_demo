from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/permissions/', views.user_permissions, name='user_permissions'),

    path('view-page/', views.protected_view_page, name='protected_view_page'),
    path('execute-page/', views.protected_execute_page, name='protected_execute_page'),
]
