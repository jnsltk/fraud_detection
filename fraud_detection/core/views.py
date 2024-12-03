from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib.auth.models import User
from .form import RegisterForm


@require_GET
def home_page(request):
    return render(request, 'home_page/index.html')

@require_GET
def get_register_form(request):
    form = RegisterForm()
    return render(request, 'registration/registration_form.html', {'form': form})

@require_POST
def post_register_form(request):
    form = RegisterForm(request.POST)
    if form.is_valid():
        return redirect('index')
    return render(request, 'registration/registration_form.html', {'form': form})
