import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from tasks.models import Priority, Category, Task, SubTask, Note

fake = Faker()

class Command(BaseCommand):
    help = 'Generate fake tasks, subtasks, and notes'

    def handle(self, *args, **options):
        priorities = list(Priority.objects.all())
        categories = list(Category.objects.all())
        statuses = ["Pending", "In Progress", "Completed"]

        if not priorities or not categories:
            self.stdout.write(self.style.WARNING('Please add Priorities and Categories first.'))
            return

        # Create 20 tasks
        for _ in range(20):
            task = Task.objects.create(
                title=fake.sentence(nb_words=5),
                description=fake.paragraph(nb_sentences=3),
                deadline=timezone.make_aware(fake.date_time_this_month()),
                status=random.choice(statuses),
                priority=random.choice(priorities),
                category=random.choice(categories),
            )

            # Create 0-3 subtasks per task
            for _ in range(random.randint(0, 3)):
                SubTask.objects.create(
                    parent_task=task,
                    title=fake.sentence(nb_words=4),
                    description=fake.paragraph(nb_sentences=2),
                    status=random.choice(statuses),
                )

            # Create 0-2 notes per task
            for _ in range(random.randint(0, 2)):
                Note.objects.create(
                    task=task,
                    content=fake.paragraph(nb_sentences=3)
                )

        self.stdout.write(self.style.SUCCESS('Fake data generated successfully!'))