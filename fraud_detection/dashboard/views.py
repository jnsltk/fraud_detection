from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.models import User


@login_required
def index(request):
    context = {
        'users_num': User.objects.count,
    }
    return render(request, 'dashboard/index.html', context=context)

def manage_models(request):
    return render(request, 'dashboard/manage_models.html')
