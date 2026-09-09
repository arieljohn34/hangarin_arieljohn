from django.contrib import admin
from .models import Priority, Category, Task, SubTask, Note

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'deadline', 'priority', 'category')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('title', 'description')

@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'parent_task_title')
    list_filter = ('status',)
    search_fields = ('title',)

    def parent_task_title(self, obj):
        return obj.parent_task.title
    parent_task_title.short_description = 'Parent Task'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Priority)
class PriorityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('task', 'content', 'created_at')  # Added 'content'
    list_filter = ('created_at',)                      # Changed from 'task' to 'created_at'
    search_fields = ('content',)