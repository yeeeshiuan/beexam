from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, IsAuthenticated
import json
import urllib
from beexam.settings import env
from beexam.utils import account_activation_token
from member.forms import UserForm, UserResetUsernameForm, UserResetPasswordForm
from member.models import User, RegisterType
from member.serializers import UserSerializer


GUEST_SAFE_METHODS = ('GET', 'POST', 'HEAD', 'OPTIONS')


class GuestUserPermission(BasePermission):
    def has_permission(self, request, view):
        return request.method in GUEST_SAFE_METHODS


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated|GuestUserPermission]

    # [POST] api/users/
    def create(self, request, **kwargs):
        formUser = UserForm(request.data)

        if formUser.is_valid():
            cleaned_data = formUser.cleaned_data
            try:
                with transaction.atomic():
                    user = User.objects.create(email=cleaned_data['email'])
                    user.set_password(cleaned_data['password'])

                    if "username" in cleaned_data:
                        user.username = cleaned_data['username']

                    user.full_clean()
                    user.save()

                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    token = account_activation_token.make_token(user)
                    body_html = render_to_string(
                        'member/email/activate-account.html',
                        {
                            'project_name': settings.PROJECT_NAME,
                            'activate_url': request.build_absolute_uri(
                                f"/activate/{uid}/{token}?email={user.email}"
                            ),
                        }
                    )
                    user.email_user(
                        "{0}: Activate your account!".format(settings.PROJECT_NAME),
                        '',
                        env('EMAIL_HOST_USER'),
                        fail_silently=False,
                        auth_user=None,
                        auth_password=None,
                        connection=None,
                        html_message=body_html
                    )
            except Exception as e:
                message = "{0}".format(e)
                message = message.replace("\n", "<br>")
                message = message.replace("\"", "'")
                return Response({
                    'success': False,
                    'errors': {
                        'others': [message]
                    }
                })

            serializer = UserSerializer(user)
            return Response({
                'success': True,
                'data': serializer.data
            })

        else:
            return Response({
                'success': False,
                'errors': dict(formUser.errors.items())
            })

    # [PATCH] api/users/pk/
    def partial_update(self, request, pk=None, **kwargs):
        action_type = request.POST.get('action')

        success = False
        errors = {'others': ["The request is not valid."]}
        if action_type == 'username':
            formUser = UserResetUsernameForm(request.data)
            if formUser.is_valid():
                cleaned_data = formUser.cleaned_data
                user = User.objects.get(pk=pk)
                user.username = cleaned_data['username']
                user.save()
                success = True
                errors = None
            else:
                errors = dict(formUser.errors.items())

        elif action_type == 'password':
            formUser = UserResetPasswordForm(request.data)
            if formUser.is_valid():
                cleaned_data = formUser.cleaned_data
                user = User.objects.get(pk=pk)
                if user.check_password(cleaned_data['password']):
                    user.set_password(cleaned_data['new_password'])
                    user.save()
                    user = authenticate(
                        request,
                        username=user.email,
                        password=cleaned_data['new_password']
                    )
                    login(request, user)
                    success = True
                    errors = None
                else:
                    errors = {'oldPassword': ["The old password is not correct."]}
            else:
                errors = dict(formUser.errors.items())

        response = {'success': success}
        if errors:
            response['errors'] = errors

        return Response(response)


def activate(request, uidb64, token):
    email = request.GET.get('email')

    user = authenticate(
            request=request,
            uidb64=uidb64,
            email=email,
            token=token
        )

    message = None
    if user is not None:
        if user.is_verified:
            message = {'danger': 'Your account has already verified! Please login.'}
        else:
            user.is_verified = True;
            user.save()
            message = {'success': 'Your account is verified! Please login.'}
    else:
        message = {'danger': 'The activated code is invalid.'}

    return render(
        request,
        'main/index.html',
        {
            'loading_message': json.dumps(message),
            'facebook_id': env('FACEBOOK_APP_ID'),
            'google_id': env('GOOGLE_APP_ID')
        }
    )


def post_login(request):
    email = request.POST.get('email')
    password = request.POST.get('password')

    user = authenticate(request, username=email, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse({'success': True})
    else:
        data = {
            'success': False,
            'errors': {
                'message': ["Sorry, that login was invalid. Please try again."]
            }
        }
        return JsonResponse(data)


@login_required
def resend_activate_email(request):
    success = False
    errors = {'message': ['The user is not login.']}

    user = request.user
    if user is not None:
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        body_html = render_to_string(
            'member/email/activate-account.html',
            {
                'project_name': settings.PROJECT_NAME,
                'activate_url': request.build_absolute_uri(
                    f"/activate/{uid}/{token}?email={user.email}"
                    ),
                }
            )
        user.email_user(
            "{0}: Activate your account!".format(settings.PROJECT_NAME),
            '',
            env('EMAIL_HOST_USER'),
            fail_silently=False,
            auth_user=None,
            auth_password=None,
            connection=None,
            html_message=body_html
        )
        success = True
        errors = None

    data = {'success': success}

    if errors:
        data['errors'] = errors

    return JsonResponse(data)


@login_required
def post_logout(request):
    logout(request)
    return JsonResponse({'success': True})


def fb_auth_callback(request):
    code = request.GET.get('code')

    # GET facebook short-term access_token
    shortTermAPIUrl = env('FACEBOOK_SHORT_TERM_API_URL')
    params = {
        "client_id": env('FACEBOOK_APP_ID'),
        "client_secret": env('FACEBOOK_APP_SECRET'),
        "redirect_uri": env('FACEBOOK_REDIRECT_URL'),
        "code": code
    }
    data = urllib.parse.urlencode(params)
    data = data.encode('ascii')
    req = urllib.request.Request(shortTermAPIUrl, data)
    with urllib.request.urlopen(req) as response:
        res = response.read()
    shortTermResData = json.loads(res)

    # GET facebook user data
    userAPIUrl = env('FACEBOOK_USER_API_URL')
    params = {
        "fields": "id,name,email",
        "access_token": shortTermResData['access_token']
    }
    data = urllib.parse.urlencode(params)
    data = data.encode('ascii')
    req = urllib.request.Request(userAPIUrl, data)
    with urllib.request.urlopen(req) as response:
        res = response.read()
    userResData = json.loads(res)

    # check if the user is exist
    user = authenticate(
        request=request,
        email=userResData['email'],
        third_party_user_id=userResData['id'],
        register_type=RegisterType.FACEBOOK.value,
    )

    message = {'success': 'Welcome Back!'}
    if user is None:
        message = {'success': 'Register Successful!'}
        try:
            with transaction.atomic():
                user = User.objects.create(email=userResData['email'])
                user.set_password('@'+userResData['id']+'@')
                user.username = userResData['name']
                user.third_party_user_id = userResData['id']
                user.register_type = RegisterType.FACEBOOK
                user.is_verified = True
                user.save()

                user = authenticate(
                    request=request,
                    email=userResData['email'],
                    third_party_user_id=userResData['id'],
                    register_type=RegisterType.FACEBOOK.value,
                )
                login(request, user)

        except Exception as e:
            message = {'danger': 'Something went wrong in the server side!'}
    else:
        login(request, user)

    return render(
        request,
        'main/index.html',
        {
            'loading_message':json.dumps(message),
            'facebook_id': env('FACEBOOK_APP_ID'),
            'google_id': env('GOOGLE_APP_ID')
        }
    )


def google_auth_callback(request):
    code = request.GET.get('code')

    # POST google for getting id_token
    accessTokenAPIUrl = env('GOOGLE_ACCESS_TOKEN_API_URL')
    params = {
        "client_id": env('GOOGLE_APP_ID'),
        "client_secret": env('GOOGLE_APP_SECRET'),
        "redirect_uri": env('GOOGLE_REDIRECT_URL'),
        "code": code,
        "grant_type": "authorization_code"
    }
    data = urllib.parse.urlencode(params)
    data = data.encode('ascii')
    req = urllib.request.Request(accessTokenAPIUrl, data)
    with urllib.request.urlopen(req) as response:
        res = response.read()
    accessTokenResData = json.loads(res)

    # GET google user data
    userDataAPIUrl = env('GOOGLE_USER_API_URL')
    params = {
        "id_token": accessTokenResData['id_token']
    }
    data = urllib.parse.urlencode(params)
    data = data.encode('ascii')
    req = urllib.request.Request(userDataAPIUrl, data)
    with urllib.request.urlopen(req) as response:
        res = response.read()
    userDataResData = json.loads(res)

    # check if the user is exist
    user = authenticate(
        request=request,
        email=userDataResData['email'],
        third_party_user_id=userDataResData['sub'],
        register_type=RegisterType.GOOGLE.value,
    )

    message = {'success': 'Welcome Back!'}
    if user is None:
        message = {'success': 'Register Successful!'}
        try:
            with transaction.atomic():
                user = User.objects.create(email=userDataResData['email'])
                user.set_password('@'+userDataResData['sub']+'@')
                user.username = userDataResData['name']
                user.third_party_user_id = userDataResData['sub']
                user.register_type = RegisterType.GOOGLE
                user.is_verified = True
                user.save()

                user = authenticate(
                    request=request,
                    email=userDataResData['email'],
                    third_party_user_id=userDataResData['sub'],
                    register_type=RegisterType.GOOGLE.value,
                )
                login(request, user)

        except Exception as e:
            print(e)
            message = {'danger': 'Something went wrong in the server side!'}
    else:
        login(request, user)

    return render(
        request,
        'main/index.html',
        {
            'loading_message':json.dumps(message),
            'facebook_id': env('FACEBOOK_APP_ID'),
            'google_id': env('GOOGLE_APP_ID')
        }
    )
