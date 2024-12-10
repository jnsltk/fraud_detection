import os

from datetime import date, datetime
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, QueryDict
from django.shortcuts import render
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.db.models.functions import Concat
from django.db.models import Value
from django.db.models import Max

from core.predictor_singleton import PredictorSingleton
from detector.models import FraudDetectionModel
from dashboard.forms import NewModelForm
from detector.services.ml_pipeline import make_model

# Define the size of the dataset to use for training
SAMPLE_SIZE = 50000


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
        View to show and train models.
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

            temp_file_path = "/tmp/tmp_model.keras"
            try:
                # Call the make_model function from the ml_pipeline service
                result = make_model(start_data_date=start_date, end_data_date=end_date, sample_size=SAMPLE_SIZE)

                # Bump up model version
                highest_version = FraudDetectionModel.objects.aggregate(max_version=Max('version'))
                version_num = highest_version.get('max_version')
                version_bump = f"v{round(float(version_num[1:]) + 0.1, 2)}"

                # Save the model to a temporary file
                result.model.save(temp_file_path)

                # Read model file
                with open(temp_file_path, 'rb') as f:
                    model_bin = f.read()

                # Save the model to the database
                model = FraudDetectionModel(version=version_bump,
                                            date_created=datetime.now(),
                                            created_by=request.user,
                                            dataset_size=result.true_sample_size,
                                            training_data_start_date=start_date,
                                            training_data_end_date=end_date,
                                            score=result.test_result['weighted avg']['f1-score'],
                                            detailed_performance=result.test_result,
                                            metadata=result.metadata,
                                            model_file=model_bin,
                                            is_deployed=False)

                model.save()

                context.update({
                    'desc':
                    'Success!',
                    'message':
                    'Congratulations! You\'ve just trained a new model! Click \'Deploy\' if you want to use it.'
                })
            except Exception as e:
                context.update({'desc': 'Uh oh, something went wrong.', 'message': 'Detailed information: \n' + str(e)})
            finally:
                # Clean up the temporary file
                if os.path.isfile(temp_file_path):
                    os.remove(temp_file_path)

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
    return HttpResponse("""<div id="dialog"></div>""")


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

    # Create new predictor instance with selected model
    if selected_model_id is not None:
        PredictorSingleton.get_instance().change_model(selected_model_id)
    else:
        # Should never happen
        raise Exception("Invalid HTML request")
    # Change the is_deployed flag for the selected model and update the database
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
    context = {'models': load_models()}
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

    context = {'models': load_models()}
    return render(request, 'dashboard/model_table.html', context=context)


def load_models():
    """
        Helper function to load models for the dashboard.
    """
    return list(
        # Annotate the full name of the user who created the model
        FraudDetectionModel.objects.annotate(created_by_full_name=Concat('created_by__first_name', Value(' '),
                                                                         'created_by__last_name')
                                             # Select only the necessary fields
                                             ).values('id', 'version', 'date_created', 'created_by_full_name',
                                                      'dataset_size', 'score', 'is_deployed'
                                                      # Order by version and date created in descending order
                                                      ).order_by('-version', '-date_created'))
