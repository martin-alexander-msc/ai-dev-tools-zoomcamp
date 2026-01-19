from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='todo_list_index'),
    path('create/', views.create, name='todo_list_create'),
    path('<int:todo_id>/edit/', views.edit, name='todo_list_edit'),
    path('<int:todo_id>/toggle/', views.toggle_resolved, name='todo_list_toggle'),
    path('<int:todo_id>/delete/', views.delete, name='todo_list_delete'),
]
