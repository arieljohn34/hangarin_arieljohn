# tasks/urls.py
from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Home
    path('', views.HomeView.as_view(), name='home'),

    # Task CRUD
    path('tasks/', views.TaskListView.as_view(), name='task_list'),
    path('tasks/create/', views.TaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/update/', views.TaskUpdateView.as_view(), name='task_update'),
    path('tasks/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),

    # Category CRUD
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),

    # Priority CRUD
    path('priorities/', views.PriorityListView.as_view(), name='priority_list'),
    path('priorities/create/', views.PriorityCreateView.as_view(), name='priority_create'),
    path('priorities/<int:pk>/update/', views.PriorityUpdateView.as_view(), name='priority_update'),
    path('priorities/<int:pk>/delete/', views.PriorityDeleteView.as_view(), name='priority_delete'),

    # Note CRUD (nested under Task, but we keep simple)
    path('notes/', views.NoteListView.as_view(), name='note_list'),
    path('notes/create/', views.NoteCreateView.as_view(), name='note_create'),
    path('notes/<int:pk>/update/', views.NoteUpdateView.as_view(), name='note_update'),
    path('notes/<int:pk>/delete/', views.NoteDeleteView.as_view(), name='note_delete'),

    # SubTask CRUD
    path('subtasks/', views.SubTaskListView.as_view(), name='subtask_list'),
    path('subtasks/create/', views.SubTaskCreateView.as_view(), name='subtask_create'),
    path('subtasks/<int:pk>/update/', views.SubTaskUpdateView.as_view(), name='subtask_update'),
    path('subtasks/<int:pk>/delete/', views.SubTaskDeleteView.as_view(), name='subtask_delete'),
]