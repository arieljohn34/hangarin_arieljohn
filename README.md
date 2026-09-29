# Hangarin - Task Management System

Hangarin is a web-based task management application built with Django. It helps users organize their daily activities, track progress, and manage deadlines through an intuitive dashboard.

## 📂 Project Structure

Here is an overview of the project's directory structure:


hangarin_project/
│
├── hangarinproj/           # Main Django project configuration
│   ├── __init__.py
│   ├── asgi.py             # ASGI config for deployment
│   ├── settings.py         # Global project settings (DB, Apps, Middleware)
│   ├── urls.py             # Main URL routing
│   └── wsgi.py             # WSGI config for deployment
│
├── tasks/                  # Main Django application (Hangarin logic)
│   ├── management/         # Custom management commands (e.g., populating default data)
│   ├── migrations/         # Database migration files
│   ├── static/             # App-specific static files
│   │   ├── css/            # Stylesheets specific to the tasks app
│   │   ├── fonts/          # Font files
│   │   ├── img/            # Images
│   │   ├── js/             # JavaScript files
│   │   └── sass/           # SASS/SCSS source files
│   ├── __init__.py
│   ├── admin.py            # Django Admin configuration
│   ├── context_processors.py # Custom context data available to all templates
│   ├── models.py           # Database models (Task, SubTask, Category, Priority, Note, Profile)
│   ├── urls.py             # App-specific URL routes
│   └── views.py            # Application logic and request handling
│
├── templates/              # Global HTML templates
│   ├── account/            # Authentication related templates (login, signup, etc.)
│   ├── category/           # Templates for managing categories
│   ├── includes/           # Reusable template partials (sidebar, navbar, etc.)
│   ├── note/               # Templates for notes
│   ├── priority/           # Templates for priorities
│   ├── profile/            # User profile templates
│   ├── socialaccount/      # Templates for social authentication (Google, GitHub)
│   ├── subtask/            # Templates for subtasks
│   ├── tasks/              # Templates for the main tasks
│   ├── base.html           # Base template that all other templates extend
│   ├── dashboard.html      # Main dashboard view
│   └── home.html           # Landing/Home page
│
├── staticfiles/            # Static files collected for production (CSS, JS, Admin)
│   ├── account/
│   ├── admin/
│   ├── css/
│   ├── fonts/
│   ├── images/
│   ├── img/
│   ├── js/
│   └── sass/
│

├── db.sqlite3              # SQLite Database (development)
├── manage.py               # Django's command-line utility
└── requirements.txt        # Python dependencies

