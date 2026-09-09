# tasks/views.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from .models import Task, Category, Priority, Note, SubTask

# ---------- Home ----------
class HomeView(TemplateView):
    template_name = 'home.html'
    def get(self, request, *args, **kwargs):
        print(f"🔍 HomeView: template_name = {self.template_name}")
        return super().get(request, *args, **kwargs)

# ---------- Task ----------
class TaskListView(ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'

class TaskCreateView(CreateView):
    model = Task
    fields = ['title', 'description', 'deadline', 'status', 'category', 'priority']
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:task_list')

class TaskUpdateView(UpdateView):
    model = Task
    fields = ['title', 'description', 'deadline', 'status', 'category', 'priority']
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:task_list')

class TaskDeleteView(DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('tasks:task_list')

# ---------- Category ----------
class CategoryListView(ListView):
    model = Category
    template_name = 'category/category_list.html'
    context_object_name = 'categories'

class CategoryCreateView(CreateView):
    model = Category
    fields = ['name']
    template_name = 'category/category_form.html'
    success_url = reverse_lazy('tasks:category_list')

class CategoryUpdateView(UpdateView):
    model = Category
    fields = ['name']
    template_name = 'category/category_form.html'
    success_url = reverse_lazy('tasks:category_list')

class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'category/category_confirm_delete.html'
    success_url = reverse_lazy('tasks:category_list')

# ---------- Priority ----------
class PriorityListView(ListView):
    model = Priority
    template_name = 'priority/priority_list.html'
    context_object_name = 'priorities'

class PriorityCreateView(CreateView):
    model = Priority
    fields = ['name']
    template_name = 'priority/priority_form.html'
    success_url = reverse_lazy('tasks:priority_list')

class PriorityUpdateView(UpdateView):
    model = Priority
    fields = ['name']
    template_name = 'priority/priority_form.html'
    success_url = reverse_lazy('tasks:priority_list')

class PriorityDeleteView(DeleteView):
    model = Priority
    template_name = 'priority/priority_confirm_delete.html'
    success_url = reverse_lazy('tasks:priority_list')

# ---------- Note ----------
class NoteListView(ListView):
    model = Note
    template_name = 'note/note_list.html'
    context_object_name = 'notes'

class NoteCreateView(CreateView):
    model = Note
    fields = ['task', 'content']
    template_name = 'note/note_form.html'
    success_url = reverse_lazy('tasks:note_list')

class NoteUpdateView(UpdateView):
    model = Note
    fields = ['task', 'content']
    template_name = 'note/note_form.html'
    success_url = reverse_lazy('tasks:note_list')

class NoteDeleteView(DeleteView):
    model = Note
    template_name = 'note/note_confirm_delete.html'
    success_url = reverse_lazy('tasks:note_list')

# ---------- SubTask ----------
class SubTaskListView(ListView):
    model = SubTask
    template_name = 'subtask/subtask_list.html'
    context_object_name = 'subtasks'

class SubTaskCreateView(CreateView):
    model = SubTask
    fields = ['parent_task', 'title', 'description', 'status']
    template_name = 'subtask/subtask_form.html'
    success_url = reverse_lazy('tasks:subtask_list')

class SubTaskUpdateView(UpdateView):
    model = SubTask
    fields = ['parent_task', 'title', 'description', 'status']
    template_name = 'subtask/subtask_form.html'
    success_url = reverse_lazy('tasks:subtask_list')

class SubTaskDeleteView(DeleteView):
    model = SubTask
    template_name = 'subtask/subtask_confirm_delete.html'
    success_url = reverse_lazy('tasks:subtask_list')