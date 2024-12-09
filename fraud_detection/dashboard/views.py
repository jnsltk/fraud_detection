import json
import os
import time

from datetime import date
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, QueryDict
from django.shortcuts import render
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.db.models.functions import Concat
from django.db.models import Value
from django.db.models import Max

from detector.models import FraudDetectionModel
from dashboard.forms import NewModelForm


@login_required
@staff_member_required
def index(request):
    """
        The main dashboard view, only accessible to staff users.
    """
    context = {
        'version': FraudDetectionModel.objects.filter(is_deployed=True).first().version or "N/A",
        'accuracy': FraudDetectionModel.objects.filter(is_deployed=True).first().score or "N/A",
        'users_num': User.objects.count,
    }
    return render(request, 'dashboard/index.html', context=context)


@login_required
@staff_member_required
@require_http_methods(['GET', 'POST'])
def manage_models(request):
    """
        View to show and train models. Incomplete for now, will be updated with
        model training pipeline.
    """

    # Define context to pass to the template
    context = {}

    # Handle form submission (Model training)
    if request.method == "POST":
        form = NewModelForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            # Call start model training pipeline here, passing in the selected dates

            # Simulate model creation
            try:
                # Bump up model version
                highest_version = FraudDetectionModel.objects.aggregate(max_version=Max('version'))
                version_num = highest_version.get('max_version')
                version_bump = f"v{round(float(version_num[1:-6]) + 0.1, 2)}-dummy"

                # Simulate model training time
                time.sleep(3)
                # Simulate model file
                random_data = os.urandom(1024)
                dummy_model = FraudDetectionModel(
                    version=version_bump,
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

                context.update({
                    'desc': 'Success!',
                    'message': 'Congratulations! You\'ve just trained a new model! Click \'Deploy\' if you want to use it.'
                })
            except Exception as e:
                context.update({
                    'desc': 'Uh oh, something went wrong.',
                    'message': 'Detailed information: \n' + str(e)
                })
        # Load models into context, so it shows up behind the modal
        context.update({'models': load_models()})
        return render(request, 'dashboard/train_model_result.html', context=context)
    else:
        # Handle GET request (Show models)
        context.update({'models': load_models()})
        return render(request, 'dashboard/manage_models.html', context=context)


@login_required
@staff_member_required
def train_model_form(request):
    """
        View to show the model training form. Only used for HTMX.
    """
    form = NewModelForm()
    return render(request, 'dashboard/train_model_form.html', {
        'form': form,
    })


@login_required
@staff_member_required
def dismiss_modal(request):
    """
        View to dismiss the model training form. Only used for HTMX.
    """
    return HttpResponse(
        """<div id="dialog"></div>"""
    )


@login_required
@staff_member_required
def train_model_result(request):
    """
        View to show the result of the model training. Only used for HTMX.
    """
    return render(request, 'dashboard/train_model_result.html')


@login_required
@staff_member_required
def deploy_model(request):
    """
        View to deploy a model. Only used for HTMX.
    """

    # Get the id of the model to deploy from the POST request
    selected_model_id = request.POST.get('deploy_id')
    selected_model = FraudDetectionModel.objects.get(id=selected_model_id)
    # Check if there is already a deployed model
    try:
        deployed_model = FraudDetectionModel.objects.get(is_deployed=True)
        if deployed_model != selected_model:
            # If there is a deployed model, undeploy it
            deployed_model.is_deployed = False
            deployed_model.save()
    except Exception as e:
        # If there is no deployed model, log the exception
        print('No deployed model found\n', e)
    # Deploy the selected model
    selected_model.is_deployed = True
    selected_model.save()
    context = {
        'models': load_models()
    }
    return render(request, 'dashboard/model_table.html', context=context)

@login_required
@staff_member_required
def delete_model(request):
    """
        View to delete a model. Only used for HTMX.
    """

    # Get the id of the model to delete from the request
    selected_model_id = request.POST.get('delete_id')
    print(selected_model_id)
    selected_model = FraudDetectionModel.objects.get(id=selected_model_id)
    selected_model.delete()

    context = {
        'models': load_models()
    }
    return render(request, 'dashboard/model_table.html', context=context)

def load_models():
    """
        Helper function to load models for the dashboard.
    """
    return list(
        # Annotate the full name of the user who created the model
        FraudDetectionModel.objects.annotate(
            created_by_full_name=Concat(
                'created_by__first_name',
                Value(' '),
                'created_by__last_name'
            )
        # Select only the necessary fields
        ).values(
            'id',
            'version',
            'date_created',
            'created_by_full_name',
            'dataset_size',
            'score',
            'is_deployed'
        # Order by version and date created in descending order
        ).order_by('-version', '-date_created')
    )
