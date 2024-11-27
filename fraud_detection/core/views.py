from django.shortcuts import render

def index(request):
    context = {
        'message': "hellooo"
    }

    return render(request, 'index.html', context=context)
