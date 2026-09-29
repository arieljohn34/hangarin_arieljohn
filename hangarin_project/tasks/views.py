# tasks/views.py
import re

from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from .models import Task, Category, Priority, Note, SubTask, Profile


# =========================================================
# Hash-based search (inverted index)
# =========================================================
def _tokenize(text):
    """Split text into lowercase alphanumeric tokens."""
    return re.findall(r'\w+', (text or '').lower())


def build_search_index(user):
    """
    Build a hash table (dict) mapping token -> list of objects, per model.
    This is an inverted index: lookup is O(1) per token.
    """
    index = {
        'task':     {},
        'category': {},
        'priority': {},
        'note':     {},
        'subtask':  {},
    }

    for task in Task.objects.filter(owner=user).only('id', 'title'):
        for tok in set(_tokenize(task.title)):
            index['task'].setdefault(tok, []).append(task)

    for cat in Category.objects.filter(owner=user).only('id', 'name'):
        for tok in set(_tokenize(cat.name)):
            index['category'].setdefault(tok, []).append(cat)

    for prio in Priority.objects.filter(owner=user).only('id', 'name'):
        for tok in set(_tokenize(prio.name)):
            index['priority'].setdefault(tok, []).append(prio)

    for note in Note.objects.filter(task__owner=user).select_related('task'):
        for tok in set(_tokenize(note.task.title)):
            index['note'].setdefault(tok, []).append(note)

    for sub in SubTask.objects.filter(parent_task__owner=user).select_related('parent_task'):
        for tok in set(_tokenize(sub.parent_task.title)):
            index['subtask'].setdefault(tok, []).append(sub)

    return index


def search_index(index, query):
    """
    Look up query tokens in the inverted index.
    Returns items matching ANY of the query tokens (union).
    """
    tokens = _tokenize(query)
    if not tokens:
        return {k: [] for k in index}

    results = {}
    for kind, table in index.items():
        seen_pks = set()
        matches = []
        for tok in tokens:
            for obj in table.get(tok, []):
                if obj.pk not in seen_pks:
                    seen_pks.add(obj.pk)
                    matches.append(obj)
        results[kind] = matches
    return results


# =========================================================
# Dashboard  (per-user) + hash search
# =========================================================
@login_required
@never_cache
def dashboard(request):
    Task.update_overdue(request.user)

    tasks = Task.objects.filter(owner=request.user)
    today = timezone.now().date()
    context = {
        'total_tasks':  tasks.count(),
        'completed':    tasks.filter(status='Completed').count(),
        'pending':      tasks.filter(status='Pending').count(),
        'overdue':      tasks.filter(status='Overdue').count(),
        'recent_tasks': tasks.order_by('-id')[:5],
    }

    # ---------- Search ----------
    query = request.GET.get('q', '').strip()
    if query:
        index = build_search_index(request.user)
        results = search_index(index, query)
        context.update({
            'query': query,
            'search_results': results,
            'search_total': sum(len(v) for v in results.values()),
        })

    return render(request, 'dashboard.html', context)


# =========================================================
# Home
# =========================================================
class HomeView(TemplateView):
    template_name = 'home.html'


# =========================================================
# Profile
# =========================================================
@login_required
def profile(request):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        bio = request.POST.get("bio", "").strip()
        profile_obj.bio = bio
        profile_obj.save()
        messages.success(request, "Profile bio saved.")
        return redirect("tasks:profile")
    return render(request, "profile/profile.html", {"profile": profile_obj})


# =========================================================
# Task  (PER-USER)
# =========================================================
@method_decorator(never_cache, name='dispatch')
class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 10

    def get_queryset(self):
        Task.update_overdue(self.request.user)
        return Task.objects.filter(owner=self.request.user).order_by('-id')


class TaskCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'deadline', 'status', 'category', 'priority']
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:task_list')
    success_message = 'Task "%(title)s" was created successfully.'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['category'].queryset = Category.objects.filter(owner=self.request.user)
        form.fields['priority'].queryset = Priority.objects.filter(owner=self.request.user)
        return form

    def form_valid(self, form):
        form.instance.owner = self.request.user
        if (form.instance.deadline
                and form.instance.deadline < timezone.now()
                and form.instance.status in ('Pending', 'In Progress')):
            form.instance.status = 'Overdue'
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'deadline', 'status', 'category', 'priority']
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:task_list')
    success_message = 'Task "%(title)s" was updated successfully.'

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['category'].queryset = Category.objects.filter(owner=self.request.user)
        form.fields['priority'].queryset = Priority.objects.filter(owner=self.request.user)
        return form

    def form_valid(self, form):
        if (form.instance.deadline
                and form.instance.deadline < timezone.now()
                and form.instance.status in ('Pending', 'In Progress')):
            form.instance.status = 'Overdue'
        return super().form_valid(form)


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('tasks:task_list')

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        title = self.object.title
        response = super().form_valid(form)
        messages.success(self.request, f'Task "{title}" was deleted.')
        return response


# =========================================================
# Category  (PER-USER)
# =========================================================
@method_decorator(never_cache, name='dispatch')
class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'category/category_list.html'
    context_object_name = 'categories'
    paginate_by = 10

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user).order_by('-id')


class CategoryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Category
    fields = ['name']
    template_name = 'category/category_form.html'
    success_url = reverse_lazy('tasks:category_list')
    success_message = 'Category "%(name)s" was created successfully.'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Category
    fields = ['name']
    template_name = 'category/category_form.html'
    success_url = reverse_lazy('tasks:category_list')
    success_message = 'Category "%(name)s" was updated successfully.'

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'category/category_confirm_delete.html'
    success_url = reverse_lazy('tasks:category_list')

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        name = self.object.name
        response = super().form_valid(form)
        messages.success(self.request, f'Category "{name}" was deleted.')
        return response


# =========================================================
# Priority  (PER-USER)
# =========================================================
@method_decorator(never_cache, name='dispatch')
class PriorityListView(LoginRequiredMixin, ListView):
    model = Priority
    template_name = 'priority/priority_list.html'
    context_object_name = 'priorities'
    paginate_by = 10

    def get_queryset(self):
        return Priority.objects.filter(owner=self.request.user).order_by('-id')


class PriorityCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Priority
    fields = ['name']
    template_name = 'priority/priority_form.html'
    success_url = reverse_lazy('tasks:priority_list')
    success_message = 'Priority "%(name)s" was created successfully.'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class PriorityUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Priority
    fields = ['name']
    template_name = 'priority/priority_form.html'
    success_url = reverse_lazy('tasks:priority_list')
    success_message = 'Priority "%(name)s" was updated successfully.'

    def get_queryset(self):
        return Priority.objects.filter(owner=self.request.user)


class PriorityDeleteView(LoginRequiredMixin, DeleteView):
    model = Priority
    template_name = 'priority/priority_confirm_delete.html'
    success_url = reverse_lazy('tasks:priority_list')

    def get_queryset(self):
        return Priority.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        name = self.object.name
        response = super().form_valid(form)
        messages.success(self.request, f'Priority "{name}" was deleted.')
        return response


# =========================================================
# Note  (PER-USER — via Task owner)
# =========================================================
@method_decorator(never_cache, name='dispatch')
class NoteListView(LoginRequiredMixin, ListView):
    model = Note
    template_name = 'note/note_list.html'
    context_object_name = 'notes'
    paginate_by = 10

    def get_queryset(self):
        return Note.objects.filter(task__owner=self.request.user).order_by('-id')


class NoteCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Note
    fields = ['task', 'content']
    template_name = 'note/note_form.html'
    success_url = reverse_lazy('tasks:note_list')
    success_message = 'Note was created successfully.'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['task'].queryset = Task.objects.filter(owner=self.request.user)
        return form


class NoteUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Note
    fields = ['task', 'content']
    template_name = 'note/note_form.html'
    success_url = reverse_lazy('tasks:note_list')
    success_message = 'Note was updated successfully.'

    def get_queryset(self):
        return Note.objects.filter(task__owner=self.request.user)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['task'].queryset = Task.objects.filter(owner=self.request.user)
        return form


class NoteDeleteView(LoginRequiredMixin, DeleteView):
    model = Note
    template_name = 'note/note_confirm_delete.html'
    success_url = reverse_lazy('tasks:note_list')

    def get_queryset(self):
        return Note.objects.filter(task__owner=self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Note was deleted.')
        return response


# =========================================================
# SubTask  (PER-USER — via parent Task owner)
# =========================================================
@method_decorator(never_cache, name='dispatch')
class SubTaskListView(LoginRequiredMixin, ListView):
    model = SubTask
    template_name = 'subtask/subtask_list.html'
    context_object_name = 'subtasks'
    paginate_by = 10

    def get_queryset(self):
        return SubTask.objects.filter(parent_task__owner=self.request.user).order_by('-id')


class SubTaskCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = SubTask
    fields = ['parent_task', 'title', 'description', 'status']
    template_name = 'subtask/subtask_form.html'
    success_url = reverse_lazy('tasks:subtask_list')
    success_message = 'SubTask "%(title)s" was created successfully.'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['parent_task'].queryset = Task.objects.filter(owner=self.request.user)
        return form


class SubTaskUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = SubTask
    fields = ['parent_task', 'title', 'description', 'status']
    template_name = 'subtask/subtask_form.html'
    success_url = reverse_lazy('tasks:subtask_list')
    success_message = 'SubTask "%(title)s" was updated successfully.'

    def get_queryset(self):
        return SubTask.objects.filter(parent_task__owner=self.request.user)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['parent_task'].queryset = Task.objects.filter(owner=self.request.user)
        return form


class SubTaskDeleteView(LoginRequiredMixin, DeleteView):
    model = SubTask
    template_name = 'subtask/subtask_confirm_delete.html'
    success_url = reverse_lazy('tasks:subtask_list')

    def get_queryset(self):
        return SubTask.objects.filter(parent_task__owner=self.request.user)

    def form_valid(self, form):
        title = self.object.title
        response = super().form_valid(form)
        messages.success(self.request, f'SubTask "{title}" was deleted.')
        return response