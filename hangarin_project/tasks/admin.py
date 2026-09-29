from django.contrib import admin
from .models import Task, Category, Priority, Note, SubTask, Profile


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'status', 'category', 'priority', 'deadline')
    list_filter = ('status', 'owner')
    search_fields = ('title', 'description')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner')
    list_filter = ('owner',)


@admin.register(Priority)
class PriorityAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner')
    list_filter = ('owner',)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('task', 'created_at')
    search_fields = ('content',)


@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'parent_task', 'status')
    list_filter = ('status',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')