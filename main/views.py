from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from beexam.settings import env


def index(request):
    return render(
        request,
        'main/index.html',
        {
            'loading_message':'',
            'facebook_id': env('FACEBOOK_APP_ID'),
            'google_id': env('GOOGLE_APP_ID')
        }
    )

def privacy_policies(request):
    return render(request, 'main/privacy-policies.html')

@login_required(login_url='/')
def dashboard(request):
    return render(
        request,
        'main/dashboard.html',
        {
            'loading_message':'',
            'facebook_id': env('FACEBOOK_APP_ID'),
            'google_id': env('GOOGLE_APP_ID')
        }
    )

@login_required(login_url='/')
def profile(request):
    return render(
        request,
        'main/profile.html',
        {
            'loading_message':'',
            'facebook_id': env('FACEBOOK_APP_ID'),
            'google_id': env('GOOGLE_APP_ID')
        }
    )
