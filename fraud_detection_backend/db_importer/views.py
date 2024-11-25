from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from db_importer.forms import CSVUploadForm
from db_importer.services.csv_handler import process_csv
from detector.models import Transaction

# Disable CSRF validation until that's set up properly
@csrf_exempt
@require_http_methods(['POST'])
def import_csv_to_db(request):
    form = CSVUploadForm(request.POST, request.FILES)
    if form.is_valid():
        csv_file = form.cleaned_data['csv_file']
        try:
            process_csv(csv_file)
            return JsonResponse({'message': 'Imported successfully!'})
        except Exception as e:
            return JsonResponse({
                'message': 'Error processing CSV file',
                'error': e
            })
    else:
        return JsonResponse({'message': 'Invalid file'})

