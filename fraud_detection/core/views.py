from django.shortcuts import render

def index(request):
    context = {
        'message': "hellooo"
    }

    return render(request, 'core/index.html', context=context)
