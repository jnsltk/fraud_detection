from django.shortcuts import render

def index(request):
    context = {
        'message': "dashboard hell yeah"
    }

    return render(request, 'dashboard/index.html', context=context)
