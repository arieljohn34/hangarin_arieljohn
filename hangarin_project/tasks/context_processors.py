# tasks/context_processors.py
from .models import Task, Category, Priority, Note, SubTask


def sidebar_counts(request):
    if not request.user.is_authenticated:
        return {}
    u = request.user
    return {
        'count_tasks':      Task.objects.filter(owner=u).count(),
        'count_categories': Category.objects.filter(owner=u).count(),
        'count_priorities': Priority.objects.filter(owner=u).count(),
        'count_notes':      Note.objects.filter(task__owner=u).count(),
        'count_subtasks':   SubTask.objects.filter(parent_task__owner=u).count(),
    }