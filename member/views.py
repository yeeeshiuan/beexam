from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, IsAuthenticated
from traceback import format_exception
from smtplib import SMTPException
import sys
from beexam.settings import env
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
                    user = User.objects.create(email=cleaned_data['email'], is_active=False)
                    user.set_password(cleaned_data['password'])

                    if "username" in cleaned_data:
                        user.username = cleaned_data['username']

                    user.full_clean()
                    user.save()

                    user.email_user(
                        'Subject here',
                        'Here is the message.',
                        env('EMAIL_HOST_USER'),
                        fail_silently=False,
                        auth_user=None,
                        auth_password=None,
                        connection=None,
                        html_message='<p>This is html message.</p><br /><b>bold</b>'
                    )
            except ValidationError as e:
                return Response({'error': str(e), 'type':'ValidationError'})
                #exc_info = sys.exc_info()
                #return Response({'error': ''.join(format_exception(*exc_info))})
            except IntegrityError as e:
                return Response({'error': str(e), 'type':'IntegrityError'})
                #exc_info = sys.exc_info()
                #return Response({'error': ''.join(format_exception(*exc_info))})
            except SMTPException as e:
                return Response({'error': str(e), 'type':'SMTPException'})
                #exc_info = sys.exc_info()
                #return Response({'error': ''.join(format_exception(*exc_info))})
            except Exception as e:
                return Response({'error': str(e), 'type':'There has been a unknown error in the database'})

            serializer = UserSerializer(user)
            return Response(serializer.data)

        else:
            return Response({
                'success': False,
                'errors': dict(formUser.errors.items())
            })
