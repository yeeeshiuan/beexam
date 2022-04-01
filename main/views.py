from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, 'main/index.html', {'loadingMessage':''})

@login_required(login_url='/')
def dashboard(request):
    return render(request, 'main/dashboard.html', {'loadingMessage':''})

@login_required(login_url='/')
def profile(request):
    return render(request, 'main/profile.html', {'loadingMessage':''})
