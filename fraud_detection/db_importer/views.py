from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.urls import reverse

from db_importer.forms import CSVUploadForm
from db_importer.services.csv_handler import process_csv
from detector.models import Transaction

@login_required
@require_http_methods(['GET', 'POST'])
def import_csv_to_db(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            try:
                # Call the process_csv function
                result = process_csv(csv_file)

                # Redirect based on validation result
                if result["status"] == "success":
                    return HttpResponseRedirect(reverse('success_page'))
                else:
                    return HttpResponseRedirect(reverse('failure_page'))
            except Exception as e:
                return JsonResponse({
                    'message': 'Error processing CSV file',
                    'error': e
                })
    else:
        form = CSVUploadForm()

    return render(request, 'upload.html', {'form': form})

def success_page(request):
    # Simple view or template to show a success message after upload
    return render(request, 'success.html', {'message': 'CSV file imported successfully!'})

def failure_page(request):
    # Simple view or template to show a failure message
    return render(request, 'failure.html', {'message': 'Invalid data in CSV file!'})