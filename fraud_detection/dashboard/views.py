import os
import time

from datetime import date
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.db.models.functions import Concat
from django.db.models import Value

from detector.models import FraudDetectionModel
from dashboard.forms import NewModelForm


@login_required
@staff_member_required
def index(request):
    context = {
        'users_num': User.objects.count,
    }
    return render(request, 'dashboard/index.html', context=context)

@login_required
@staff_member_required
@require_http_methods(['GET', 'POST'])
def manage_models(request):
    if request.method == "POST":
        form = NewModelForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            # Call start model training pipeline here, passing in the selected dates

            # Simulate model creation
            try:
                print(start_date, end_date)
                # Simulate model training time
                time.sleep(3)
                random_data = os.urandom(1024)
                dummy_model = FraudDetectionModel(
                    version="v3.2-dummy",
                    date_created=date.today(),
                    dataset_size=100000,
                    training_data_start_date=start_date,
                    training_data_end_date=end_date,
                    score=98.02,
                    detailed_performance={'f1-score': '98.02'},
                    metadata={'important_data': 'yes'},
                    model_file=random_data,
                    is_deployed=False,
                    created_by=request.user
                )
                dummy_model.save()

                context = {
                    'desc': 'Success!',
                    'message': 'Congratulations! You\'ve just trained a new model! Click \'Deploy\' if you want to use it.'
                }
            except Exception as e:
                context = {
                    'desc': 'Uh oh, something went wrong.',
                    'message': 'Detailed information: \n' + e
                }
        return render(request, 'dashboard/train_model_result.html', context=context)
    else:
        context = {}
        #Query model metadata from database
        model_metadata = list(
            FraudDetectionModel.objects.annotate(
                created_by_full_name=Concat(
                    'created_by__first_name',
                    Value(' '),
                    'created_by__last_name'
                )
            ).values(
                'version',
                'date_created',
                'created_by_full_name',
                'dataset_size',
                'score',
                'is_deployed'
            )
        )

        # Set first value to deployed
        model_metadata[0]['is_deployed'] = True

        context.update({'models': model_metadata})
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
