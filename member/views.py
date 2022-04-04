from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework import viewsets
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.permissions import BasePermission, IsAuthenticated
import json
from beexam.settings import env
from beexam.utils import account_activation_token
from member.forms import UserForm, UserResetUsernameForm, UserResetPasswordForm
from member.models import User
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
                        'member/email/activateAccount.html',
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
    return render(request, 'main/index.html', {'loadingMessage': json.dumps(message)})


def postLogin(request):
    email = request.POST.get('email')
    password = request.POST.get('password')

    user = authenticate(request, username=email, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse({'success': True, 'url': reverse('index')})
    else:
        data = {
            'success': False,
            'errors': {
                'message': ["Sorry, that login was invalid. Please try again."]
            }
        }
        return JsonResponse(data)


@login_required
def resendActivateEmail(request):
    success = False
    errors = {'message': ['The user is not login.']}

    user = request.user
    if user is not None:
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        body_html = render_to_string(
            'member/email/activateAccount.html',
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
def postLogout(request):
    logout(request)
    return JsonResponse({'success': True})

def fbAuthCallback(request):
    body_unicode = request.body.decode('utf-8')
    body_data = json.loads(body_unicode)
    print(body_data)
    print(json.dumps(body_data))

    message = {'success': 'FB callback successful.'}
    return render(
        request,
        'main/index.html',
        {
            'loadingMessage':json.dumps(message),
            'facebookId': env('FACEBOOK_APP_ID')
        }
    )
