from django.contrib.auth.models import User, Group
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.views import exception_handler
from member.serializers import UserSerializer
from member.forms import UserForm

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
        password = request.data.get('password')
        password_check = request.data.get('password_check')

        if not password:
            return Response({'error': 'lack of the parameters(password)'})
        elif not password_check:
            return Response({'error': 'lack of the parameters(password_check)'})
        elif password and password_check and password != password_check:
            return Response({'error': 'The two password fields didn’t match.'})

        user = User.objects.create(username=username, is_active=False)
        user.set_password(password)
        user.save()

        serializer = UserSerializer(user)

        return Response(serializer.data)


def signup(request):
    return render(request, 'signup.html')
