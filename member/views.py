from django.conf import settings
from django.contrib.auth import login, authenticate
from django.db import IntegrityError, transaction
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, IsAuthenticated
from smtplib import SMTPException
from beexam.settings import env
from beexam.utils import account_activation_token
from member.serializers import UserSerializer
from member.forms import UserForm
from member.models import User


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

def activate(request, uidb64, token):
    email = request.GET.get('email')

    user = authenticate(
            request=request,
            uidb64=uidb64,
            email=email,
            token=token
        )

    if user is not None:
        login(request, user)
    return redirect('/users/', request)
