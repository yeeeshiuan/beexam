from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from beexam.settings import env


def index(request):
    return render(
        request,
        'main/index.html',
        {
            'loadingMessage':'',
            'facebookId': env('FACEBOOK_APP_ID')
        }
    )

@login_required(login_url='/')
def dashboard(request):
    return render(
        request,
        'main/dashboard.html',
        {
            'loadingMessage':'',
            'facebookId': env('FACEBOOK_APP_ID')
        }
    )

@login_required(login_url='/')
def profile(request):
    return render(
        request,
        'main/profile.html',
        {
            'loadingMessage':'',
            'facebookId': env('FACEBOOK_APP_ID')
        }
    )
