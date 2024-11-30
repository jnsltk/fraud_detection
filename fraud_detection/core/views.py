from django.shortcuts import render

def home_page(request):
    context = {
        'message': "hellooo"
    }

    return render(request, 'home_page/index.html', context=context)
