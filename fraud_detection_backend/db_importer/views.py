from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.urls import reverse

from db_importer.forms import CSVUploadForm
from db_importer.services.csv_handler import process_csv
from detector.models import Transaction

# Disable CSRF validation until that's set up properly
@csrf_exempt
@require_http_methods(['GET', 'POST'])
def import_csv_to_db(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            try:
                process_csv(csv_file)
                return HttpResponseRedirect(reverse('success_page'))
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