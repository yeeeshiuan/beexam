from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.views import exception_handler
from traceback import format_exception
from smtplib import SMTPException
import sys
from beexam.settings import env
from member.serializers import UserSerializer
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
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        password_check = request.data.get('password_check')

        if not password:
            return Response({'error': 'lack of the parameters(password)'})
        elif not password_check:
            return Response({'error': 'lack of the parameters(password_check)'})
        elif password and password_check and password != password_check:
            return Response({'error': 'The two password fields did not match.'})

        if not email:
            return Response({'error': 'lack of the parameters(email)'})

        try:
            with transaction.atomic():
                validate_email(email)

                user = User.objects.create(email=email, is_active=False)
                user.set_password(password)
                if username:
                    user.username = username
                user.save()

                send_mail(
                    'Subject here',
                    'Here is the message.',
                    env('EMAIL_HOST_USER'),
                    [email],
                    fail_silently=False,
                    auth_user=None,
                    auth_password=None,
                    connection=None,
                    html_message='<p>This is html message.</p><br /><b>bold</b>'
                )
        except ValidationError as e:
            exc_info = sys.exc_info()
            return Response({'error': ''.join(format_exception(*exc_info))})
        except IntegrityError as e:
            exc_info = sys.exc_info()
            return Response({'error': ''.join(format_exception(*exc_info))})
        except SMTPException as e:
            exc_info = sys.exc_info()
            return Response({'error': ''.join(format_exception(*exc_info))})

        serializer = UserSerializer(user)

        return Response(serializer.data)


def signup(request):
    return render(request, 'member/signup.html')
