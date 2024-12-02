from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_POST
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
        print(form.cleaned_data)
        return redirect('home')
    return render(request, 'registration/registration_form.html', {'form': form})
