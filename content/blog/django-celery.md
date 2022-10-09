Title: Deploy a Django Celery Application with uWSGI and Nginx in Docker Compose (Pt. 1)
Date: 2022-10-04
Author: Nathan Pezzotti
Category: python
Tags: python, devops
Image: django_celery.png

This application is a basic authentication system which sends a welcome email user Celery whenever a new user registers. Part one goes over building the application and running it locally, and part two covers deploying the app in Docker Compose.

## What is Celery

Celery is a Python library which operates as a task queue. It allows you perform work outside of the HTTP request-response cycle, such as processing user input, connecting to a third-party API, or sending emails (as shown in this project) without blocking the end user from continuing to use the site. When using Celery, you will define units of work known as tasks, which are then executed asyncronously by Celery worker processes.

## Getting started

Make a project directory and change into it:
```
$ mkdir django-celery-app && cd django-celery-app
```
Start a virtual environment (substitute python3 for the path to your Python 3 interpreter):
```
$ python3 -m venv .env
```
Start the virtual environment:
```
$ source .env/bin/activate
```
Install Django:
```
(.env) $ python -m pip install -U pip django
```
Create new project called django:
```
(.env) $ django-admin startproject django_celery_app && cd django_celery_app
```
Verify the installation is working by starting the Django server and loading the default page in your browser at `http://localhost:8080`:
```
(.env) $ python manage.py runserver
```
Start a Django app which will be used for managing users:
```
(.env) $ python manage.py startapp accounts
```
Add the app to your installed apps:
```
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
]
```
Edit the accounts/models.py file to add a `DjangoCeleryAppUser` model:
```
...
from django.contrib.auth.models import AbstractUser


class DjangoCeleryAppUser(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
```
This models represents a custom user for the `django-celery-app`- for the purposes of this project, the properties of the default Django user are largely sufficient, though we'll inherit from the `AbstractUser` base class in order to customize it slightly.

The `email` property is overrode to add a unique constraint to the field so that no user will be able to have the same email. Then, the `USERNAME_FIELD` is set to `email` so that will be used for logging in. `REQUIRED_FIELDS` is set to and array with `username` only- `email` is included in it in the base class and the `USERNAME_FIELD` cannot be part of this array.

Finally, the `__str__` is overrode so that when an user instance is printed, the email is displayed.

Add a setting to the `settings.py` file so that the custom user model is used as the authentication:
```
AUTH_USER_MODEL = 'accounts.DjangoCeleryAppUser'
```
Make the migrations and migrate the database
```
(.env) $ python manage.py makemigrations
(.env) $ python manage.py migrate
```
In the `django_celery_app/urls.py` file, add these entries:
```
...
from django.urls import path, include

urlpatterns = [
    ...
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
]
```
This allows any HTTP requests to `/accounts/*` to first attempt to use any custom views in the `accounts` app, then the default auth views provided by the Django `auth` app.

Create a `urls.py` in the `accounts` directory and add the following content
```
from django.urls import path

from .views import SignUpView

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
]
```
In the `views.py` file, add the following code:
```
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView

from .forms import DjangoCeleryAppUserCreationForm


class SignUpView(SuccessMessageMixin, CreateView):
    form_class = DjangoCeleryAppUserCreationForm
    success_url = reverse_lazy('login')
    success_message = "Account successfully created!"
    template_name = 'registration/signup.html'
```
This uses the `DjangoCeleryAppUserCreationForm` as the form class. The `success_url` determines where the user will be redirected after logging in. The `success_message` will be displayed in the form, and template used to display the form is the `registration/signup.html`.

Next, create a `forms.py` file and add a `DjangoCeleryAppUserCreationForm` and the template will exist in the following `registration` folder:
```
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import DjangoCeleryAppUser


class DjangoCeleryAppUserCreationForm(UserCreationForm):
    
    password1 = forms.CharField(label='Enter password', 
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', 
                                widget=forms.PasswordInput)
    class Meta:
        model = DjangoCeleryAppUser
        fields = ("username", "email")
        help_texts = {
            "username": None,
        }

class DjangoCeleryAppUserChangeForm(UserChangeForm):

    class Meta:
        model = DjangoCeleryAppUser
        fields = ('username', 'email')
```
Theese inherit from the `UserCreationForm` and `UserChangeForm` but accomodate the customizations in the `DjangoCeleryAppUser`. The `password1` and `password2` fields are overrode to prevent the help text from showing up under the input field. The `Meta` class's `model` property specifies the `DjangoCeleryAppUser` model be used as the model. It also adds the `email` field to the fields property so that it shows up in the form and removes the default help text that appears under the input field for the username.

To use the custom `DjangoCeleryAppUserAdmin` in Django admin app, add the following in the `accounts/admin.py`:
```
...
from django.contrib.auth.admin import UserAdmin

from .forms import DjangoCeleryAppUserCreationForm, DjangoCeleryAppUserChangeForm
from .models import DjangoCeleryAppUser

class DjangoCeleryAppUserAdmin(UserAdmin):
    add_form = DjangoCeleryAppUserCreationForm
    form = DjangoCeleryAppUserChangeForm
    model = DjangoCeleryAppUser
    list_display = ('email', 'is_staff', 'is_active',)

admin.site.register(DjangoCeleryAppUser, DjangoCeleryAppUserAdmin)
```
Currently, when a user logs in, the are redirected to `/accounts/profile`, which doesn't exist in this app. Add the following to the `settings.py` file to change this to the index page:
```
LOGIN_REDIRECT_URL = "home"
```
Lastly, add this setting to the `settings.py`, so that a logout action redirects the user to the `login` view, instead of `/accounts/logout/`:
```
LOGOUT_REDIRECT_URL = "login"
```
Now that the views are defined, create a `templates/registration` directory in the base directory of the project:
```
(.env) $ python manage.py shell
>>> from django.conf import settings
>>> settings.BASE_DIR.as_posix()
'/Users/nathan.pezzotti/projects/test-django-celery-app/django_celery_app'
>>> import os
>>> os.mkdir(settings.BASE_DIR.joinpath('templates'))
>>> os.mkdir(settings.BASE_DIR.joinpath('templates/registration'))
```
Create four files in this directory, which will be the templates:
```
touch <PROJECT_ROOT>/templates/{base.html,home.html} <PROJECT_ROOT>/templates/registration/{login.html,signup.html}
```
Add the following HTML to the `base.html`
```
<html>
<head>
  <meta charset="utf-8">
  <title>{% block title %}Django-Celery App{% endblock %}</title>
</head>
<body>
  <h1>Django-Celery App</h1>
  {% block content %}
  {% endblock %}
</body>
</html>
```
This is the base HTML from which all templates will inherit. The title will be Django-Celery App, but this can be overrode in child templates with the `block title`. The `block content` is where page content will be populated.

Add the following HTML to the auth views:
`registration/login.html`:
```
{% extends "base.html" %}

{% block title %}Log In{% endblock %}

{% block content %}
<div class="container">
  <div class="account-form">
    {% if messages %}
      {% for message in messages %}
      <p{% if message.tags %} class="{{ message.tags }} message"{% endif %}>{{ message }}</p>
      {% endfor %}
    {% endif %}
    <h2>Log In</h2>
    <form method="post">
      {% csrf_token %}
      {{ form.as_p }}
      <input type="submit" value="Log In"></input>
    </form>
    <p>Don't have an account? <a href="{% url 'signup' %}">Sign up here.</a></p>
  </div>
</div>
{% endblock %}
```
`registration/signup.html`:
```
{% extends "base.html" %}

{% block title %}Sign Up{% endblock %}

{% block content %}
<div class="container">
  <div class="account-form">
    <h2>Sign up</h2>
    <form method="post">
      {% csrf_token %}
      {{ form.as_p }}
      <input type="submit" value="Sign up"></input>
    </form>
    <p>Already have an account? <a href="{% url 'login' %}">Log in.</a></p>
  </div>
</div>
{% endblock %}
```
The `login.html` template includes a `for` loop which checks for any messages- it will display the `success_message` defined in the `SignUpView` when a user is redirected to it upon a successful signup. 

For the home page, add the following HTML to the `home.html` template:
```
{% extends "base.html" %}

{% block content %}
<div class="container">
{% if user.is_authenticated %}
<div class="content">
  <h2>Hello {{ user.username }}! Thanks for logging in.</h2>
  <p><a href="{% url 'logout' %}">Log Out</a></p>
</div>
{% else %}
<div class="content">
  <h2>Hello! You are not logged in.</h2>
  <p>Please <a href="{% url 'login' %}">log in</a>  in or <a href="{% url 'signup' %}">sign up</a> if you do not have an account.</p> 
</div>
{% endif %}
</div>
{% endblock %}
```
This extends from the `base.html`, and overrides the `content` with An `if` statement checks to see if the user is authenticated and if so, displays a welcome message. Otherwise, they are prompted to log in or sign up.

In the `django_celery_app/urls.py` file, add an entry for this view:
```
...
from django.views.generic.base import TemplateView

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    ...
```
To instruct Djano to look in the root `templates` folder for templates, modify the `TEMPLATES` setting in the `settings.py` file:
```
TEMPLATES = [
    {
        ...
        "DIRS": [
            BASE_DIR / 'templates'
        ],
        ...
```
Lastly, create a `static` folder in the root folder of the project and add the content in the `styles.css` in the linked Github project and modify the `base.html` to include it as a stylesheet:
```
<head>
  ...
  <link rel="stylesheet" href="{% static 'styles.css' %}" type='text/css'>
</head>
```
In order to load styles, the following needs to be added to the top of the `base.html` as well:
```
{% load static %}
```
Add the root `static` folder to the list of static files Django will search:
```
STATICFILES_DIRS = (
    BASE_DIR / 'static',
)
```
## Install Celery

Install Celery with the dependencies for Redis:
```
pip install "celery[redis]"
```
Create a `celery.py` in the management app folder (`django_celery_app`) with the following content:
```
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_celery_app.settings")
app = Celery("django_celery_app")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
```
The `DJANGO_SETTINGS_MODULE` environment variable is set so that the Celery CLI (used later) can find the Django settings. `app` is an instance of Celery. `config_from_object` makes the app get its configuration through the Django settings, specifically those keys beginning with `CELERY_`. `app.autodiscover_tasks()` will look in each installed app for Celery tasks.

In the `django_celery_app/__init__.py`, add the following content:
```
from .celery import app as celery_app

__all__ = ('celery_app',)
```
This is required so that the app is loaded when Django starts and is available for reference by the `@shared_task` decorator 

In the `settings.py` file, add the following settings to point to the where Redis is running as a broker and backend:
```
CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/0"
```
For development purposes, you can run Redis in a container with a port mapping:
```
docker run -p 6379:6379 -d redis
```

Next, to create a task which send a new user a welcome email, creat an `accounts/tasks.py` file:
```
touch accounts/tasks.py
```
Add the following content:

```
import os
from time import sleep

from celery import shared_task
from django.core.mail import send_mail


@shared_task(name='send_welcome_email')
def send_welcome_email_task(username, email):
    """Sends a welcome email to a user when they sign up."""
    sleep(5)
    send_mail(
        f"Welcome {username}!",
        f"Hi {username},\n\nThank you for signing up for our site!\nThis email was sent by a celery worker with process ID {os.getpid()}.\n",
        "noreply@example.com",
        [email],
        fail_silently=False,
    )
```
This defines a `shared_task` named `send_welcome_email`. A `@shared_task` decorator allows for defining tasks without depending on the project-level Celery app, as tasks created outside of a Django project usually reference an app instance directly through `@app.task`. This task takes the username of the new user and the email content as arguments with which it will create the email. The The `sleep(5)` is used to make the function take some time to run, as might be the case in a real-world situation. The Django `send_email` function is used to send the email,.

So the email is printed to the console, rather than sent through an SMTP mail server, add the following setting in the `settings.py`
```
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
```
In the `accounts/forms.py` file, add the following content:
```
...
from .tasks import send_welcome_email_task


class DjangoCeleryAppUserCreationForm(UserCreationForm):
    ...

    def send_email(self):
        send_welcome_email_task.delay(self.cleaned_data["username"], self.cleaned_data["email"])
```
This adds a method to the `DjangoCeleryAppUserCreationForm` which invokes the `shared_task`, `send_welcome_email_task` using the Celery `delay` method, to execute the task asyncronously
.
In the `accounts/views.py` file, add the following function:
```
class SignUpView(SuccessMessageMixin, CreateView):
    ...

    def form_valid(self, form):
        form.send_email()
        return super().form_valid(form)
```
This overrides the `form_valid` function to call the `send_email` function in the form when a new user successfully signs up.
## Start the application:

In a separate terminal, start the virtual environment with `source .env/bin/activate` and change into the project directory.

Start Celery:

```
(.env) $ python -m celery -A django_celery_app worker
```
This command starts a Celery worker with the `worker` command, which will process the tasks.

Start the Django server:
```
(.env) $ python manage.py runserver
```
Access `http://localhost:8000/accounts/signup` and create an account- after about 5 seconds, a welcome email should be printed to the console by the Celery worker.

The full source code can be found [here](https://github.com/npezzotti/django-celery-app)