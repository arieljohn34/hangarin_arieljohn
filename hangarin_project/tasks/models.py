from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta


class Priority(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="priorities", null=True, blank=True)
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Priority"
        verbose_name_plural = "Priorities"

    def __str__(self):
        return self.name


class Category(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories", null=True, blank=True)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Task(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Completed", "Completed"),
        ("Overdue", "Overdue"),
    ]
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks", null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    deadline = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Pending")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    priority = models.ForeignKey(Priority, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self):
        return self.title

    @classmethod
    def update_overdue(cls, user):
        """
        Updates the status of tasks to 'Overdue' if their deadline has passed.
        """
        cls.objects.filter(
            owner=user,                            # <-- FIXED: Changed 'user' to 'owner'
            status__in=['Pending', 'In Progress'], # Only update tasks that aren't completed
            deadline__lt=timezone.now()            # Deadline is in the past
        ).update(status='Overdue')


class SubTask(models.Model):
    STATUS_CHOICES = Task.STATUS_CHOICES
    parent_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="subtasks")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Pending")

    class Meta:
        verbose_name = "SubTask"
        verbose_name_plural = "SubTasks"

    def __str__(self):
        return f"{self.title} (for {self.parent_task.title})"


class Note(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="notes")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"

    def __str__(self):
        return f"Note for {self.task.title} - {self.created_at.strftime('%Y-%m-%d')}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True, max_length=500, default="")

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return f"{self.user.username}'s profile"


# =========================================================
# Defaults for new users
# =========================================================
DEFAULT_CATEGORIES = ['Work', 'Personal', 'School', 'Finance', 'Projects']
DEFAULT_PRIORITIES = ['High', 'Medium', 'Low', 'Optional']

DEFAULT_TASKS = [
    # (title, category, priority, status)
    ('Review quarterly report',       'Work',     'High',   'Pending'),
    ('Buy groceries',                  'Personal', 'Low',    'Pending'),
    ('Update website layout',          'Work',     'Medium', 'In Progress'),
    ('Read a book chapter',            'Personal', 'Low',    'Pending'),
    ('Prepare for exam',               'School',   'High',   'Pending'),
    ('Pay electric bill',              'Finance',  'High',   'Pending'),
    ('Team meeting notes',             'Work',     'Medium', 'Completed'),
    ('Exercise for 30 minutes',        'Personal', 'Medium', 'Pending'),
    ('Complete assignment',            'School',   'High',   'In Progress'),
    ('Track monthly budget',           'Finance',  'Medium', 'Pending'),
    ('Refactor login code',            'Projects', 'High',   'Pending'),
    ('Water plants',                   'Personal', 'Low',    'Completed'),
    ('Study for quiz',                 'School',   'High',   'Pending'),
    ('Review savings plan',            'Finance',  'Low',    'Pending'),
    ('Set up dev environment',         'Projects', 'Medium', 'In Progress'),
    ('Reply to emails',                'Work',     'Low',    'Pending'),
    ('Call a friend',                  'Personal', 'Low',    'Pending'),
    ('Read documentation',             'School',   'Medium', 'Pending'),
    ('Backup important files',         'Finance',  'Medium', 'Pending'),
    ('Deploy latest changes',          'Projects', 'High',   'Pending'),
]

# (task_index, content)  — task_index refers to position in DEFAULT_TASKS
DEFAULT_NOTES = [
    (0,  'Include Q3 numbers and comparison with Q2.'),
    (2,  'User complained the mobile layout feels cramped.'),
    (4,  'Focus on chapter 3 — likely on the exam.'),
    (6,  'Due on the 15th, do not forget.'),
    (8,  'Submit on Moodle before midnight.'),
    (10, 'Consider using envelope method for tracking.'),
    (12, 'Refactor to class-based views if possible.'),
    (14, 'Switch to the 50/30/20 rule.'),
    (16, 'Ask team about the Docker setup.'),
    (18, 'Mark urgent ones as starred.'),
]

# (task_index, title, status)
DEFAULT_SUBTASKS = [
    (0,  'Draft outline',              'Pending'),
    (0,  'Write introduction',         'Pending'),
    (2,  'Fix navbar responsiveness',  'Pending'),
    (4,  'Review past papers',         'Pending'),
    (6,  'Share with team',            'Completed'),
    (8,  'Write first draft',          'In Progress'),
    (8,  'Proofread',                  'Pending'),
    (10, 'Log last month expenses',    'Pending'),
    (12, 'Write tests',                'Pending'),
    (14, 'Compare with last quarter',  'Pending'),
]

# Overdue defaults: (title, category, priority, days_ago)
DEFAULT_OVERDUE = [
    ('Submit late report',         'Work',     'High',   3),
    ('Pay overdue subscription',   'Finance',  'High',   5),
    ('Reply to advisor email',     'School',   'Medium', 2),
    ('Renew expired license',      'Personal', 'High',   7),
]

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

        # 1. Categories
        cats = {}
        for name in DEFAULT_CATEGORIES:
            cat, _ = Category.objects.get_or_create(owner=instance, name=name)
            cats[name] = cat

        # 2. Priorities
        prios = {}
        for name in DEFAULT_PRIORITIES:
            prio, _ = Priority.objects.get_or_create(owner=instance, name=name)
            prios[name] = prio

        # 3. Regular tasks
        tasks = []
        for title, cat_name, prio_name, status in DEFAULT_TASKS:
            task = Task.objects.create(
                owner=instance,
                title=title,
                status=status,
                category=cats.get(cat_name),
                priority=prios.get(prio_name),
            )
            tasks.append(task)

        # 3b. Overdue defaults
        for title, cat_name, prio_name, days_ago in DEFAULT_OVERDUE:
            Task.objects.create(
                owner=instance,
                title=title,
                status='Overdue',
                deadline=timezone.now() - timedelta(days=days_ago),
                category=cats.get(cat_name),
                priority=prios.get(prio_name),
            )

        # 4. Notes
        for idx, content in DEFAULT_NOTES:
            if idx < len(tasks):
                Note.objects.create(task=tasks[idx], content=content)

        # 5. Subtasks
        for idx, title, status in DEFAULT_SUBTASKS:
            if idx < len(tasks):
                SubTask.objects.create(
                    parent_task=tasks[idx],
                    title=title,
                    status=status,
                )

    instance.profile.save()