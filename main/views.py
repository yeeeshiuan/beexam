from django.shortcuts import render


def index(request):
    return render(request, 'main/index.html', {'loadingMessage':''})

def dashboard(request):
    return render(request, 'main/dashboard.html', {'loadingMessage':''})
