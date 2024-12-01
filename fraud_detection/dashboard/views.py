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
    context = {}
    # Define dummy data for now
    models = []
    for i in range(10):
        models.append({
            'version': 'v3.19',
            'date_created': '2024.11.30',
            'created_by': 'Bob McRoberts',
            'dataset_size': '100000',
            'score': '99.4',
            'deployed': False
        })
    # Set first value to deployed
    models[0]['deployed'] = True

    context.update({'models': models})
    return render(request, 'dashboard/manage_models.html', context=context)
