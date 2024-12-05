import os
import time

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from detector.models import FraudDetectionModel
from dashboard.forms import NewModelForm


@login_required
def index(request):
    context = {
        'users_num': User.objects.count,
    }
    return render(request, 'dashboard/index.html', context=context)


@require_http_methods(['GET', 'POST'])
def manage_models(request):
    if request.method == "POST":
        form = NewModelForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            # Call start model training pipeline here, passing in the selected dates

            # Simulate model creation
            print(start_date, end_date)
            # Simulate model training time
            time.sleep(3)
            random_data = os.urandom(1024)
            dummy_model = FraudDetectionModel(
                version="v3.2-dummy",
                date_created="2024-12-04",
                dataset_size=100000,
                training_data_start_date=start_date,
                training_data_end_date=end_date,
                score=98.02,
                detailed_performance={'f1-score': '98.02'},
                metadata={'important_data': 'yes'},
                model_file=random_data,
                is_deployed=True,
                created_by=request.user
            )
            dummy_model.save()

            context = {
                'desc': 'Success!',
                'message': 'Congratulations! You\'ve just trained a new model! Click \'Deploy\' if you want to use it.'
            }
        return render(request, 'dashboard/train_model_result.html', context=context)
    else:
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


def train_model_form(request):
    form = NewModelForm()
    return render(request, 'dashboard/train_model_form.html', {
        'form': form,
    })


def cancel_model_form(request):
    return HttpResponse(
        """<div id="dialog"></div>"""
    )


def train_model_result(request):
    return render(request, 'dashboard/train_model_result.html')
