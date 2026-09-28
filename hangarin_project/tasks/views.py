# tasks/views.py
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

from .models import Task, Category, Priority, Note, SubTask, Profile


# ---------- Dashboard ----------
@login_required
def dashboard(request):
    tasks = Task.objects.all()
    today = timezone.now().date()
    context = {
        'total_tasks': tasks.count(),
        'completed': tasks.filter(status='Completed').count(),
        'pending':   tasks.filter(status='Pending').count(),
        'overdue':   tasks.filter(deadline__lt=today).exclude(status='Completed').count(),
        'recent_tasks': tasks.order_by('-id')[:5],
    }
    return render(request, 'dashboard.html', context)


# ---------- Profile ----------
@login_required
def profile(request):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        bio = request.POST.get("bio", "").strip()
        profile_obj.bio = bio
        profile_obj.save()
        return redirect("tasks:profile")
    return render(request, "profile/profile.html", {"profile": profile_obj})


# ---------- Home ----------
class HomeView(TemplateView):
    template_name = 'home.html'


# ---------- Task ----------
class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 10

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'deadline', 'status', 'category', 'priority']
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:task_list')

class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'deadline', 'status', 'category', 'priority']
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:task_list')

class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('tasks:task_list')


# ---------- Category ----------
class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'category/category_list.html'
    context_object_name = 'categories'
    paginate_by = 10

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    fields = ['name']
    template_name = 'category/category_form.html'
    success_url = reverse_lazy('tasks:category_list')

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    fields = ['name']
    template_name = 'category/category_form.html'
    success_url = reverse_lazy('tasks:category_list')

class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'category/category_confirm_delete.html'
    success_url = reverse_lazy('tasks:category_list')


# ---------- Priority ----------
class PriorityListView(LoginRequiredMixin, ListView):
    model = Priority
    template_name = 'priority/priority_list.html'
    context_object_name = 'priorities'
    paginate_by = 10

class PriorityCreateView(LoginRequiredMixin, CreateView):
    model = Priority
    fields = ['name']
    template_name = 'priority/priority_form.html'
    success_url = reverse_lazy('tasks:priority_list')

class PriorityUpdateView(LoginRequiredMixin, UpdateView):
    model = Priority
    fields = ['name']
    template_name = 'priority/priority_form.html'
    success_url = reverse_lazy('tasks:priority_list')

class PriorityDeleteView(LoginRequiredMixin, DeleteView):
    model = Priority
    template_name = 'priority/priority_confirm_delete.html'
    success_url = reverse_lazy('tasks:priority_list')


# ---------- Note ----------
class NoteListView(LoginRequiredMixin, ListView):
    model = Note
    template_name = 'note/note_list.html'
    context_object_name = 'notes'
    paginate_by = 10

class NoteCreateView(LoginRequiredMixin, CreateView):
    model = Note
    fields = ['task', 'content']
    template_name = 'note/note_form.html'
    success_url = reverse_lazy('tasks:note_list')

class NoteUpdateView(LoginRequiredMixin, UpdateView):
    model = Note
    fields = ['task', 'content']
    template_name = 'note/note_form.html'
    success_url = reverse_lazy('tasks:note_list')

class NoteDeleteView(LoginRequiredMixin, DeleteView):
    model = Note
    template_name = 'note/note_confirm_delete.html'
    success_url = reverse_lazy('tasks:note_list')


# ---------- SubTask ----------
class SubTaskListView(LoginRequiredMixin, ListView):
    model = SubTask
    template_name = 'subtask/subtask_list.html'
    context_object_name = 'subtasks'
    paginate_by = 10

class SubTaskCreateView(LoginRequiredMixin, CreateView):
    model = SubTask
    fields = ['parent_task', 'title', 'description', 'status']
    template_name = 'subtask/subtask_form.html'
    success_url = reverse_lazy('tasks:subtask_list')

class SubTaskUpdateView(LoginRequiredMixin, UpdateView):
    model = SubTask
    fields = ['parent_task', 'title', 'description', 'status']
    template_name = 'subtask/subtask_form.html'
    success_url = reverse_lazy('tasks:subtask_list')

class SubTaskDeleteView(LoginRequiredMixin, DeleteView):
    model = SubTask
    template_name = 'subtask/subtask_confirm_delete.html'
    success_url = reverse_lazy('tasks:subtask_list')