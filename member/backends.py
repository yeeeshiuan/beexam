from django.contrib.auth.backends import BaseBackend
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from beexam.utils import account_activation_token  
from member.models import User, RegisterType


class CustomModelBackend(BaseBackend):
    """
    Authenticates against settings.AUTH_USER_MODEL.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        if username is None or password is None:
            return
        try:
            user = User._default_manager.get_by_natural_key(username)
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            User().set_password(password)
        else:
            if user.register_type == RegisterType.EMAIL.value:
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user


class ActivateBackend(BaseBackend):
    def authenticate(self, request, uidb64=None, email=None, token=None, **kwargs):
        if uidb64 is None:
            return
        if token is None:
            return

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid, email=email)
        except Exception:
            return None

        if user is None:
            return None

        if account_activation_token.check_token(user, token):
            return user
        else:
            return None

    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        is_active = getattr(user, "is_active", None)
        return is_active or is_active is None


class ThirdPartyBackend(BaseBackend):
    def authenticate(self, request, email=None, third_party_user_id=None, register_type=None, **kwargs):
        if third_party_user_id is None:
            return

        if register_type is None or register_type == RegisterType.EMAIL.value:
            return

        try:
            user = User.objects.get(
                email=email,
                third_party_user_id=third_party_user_id,
                register_type=register_type
            )
        except Exception:
            return None

        if user is None:
            return None

        return user

    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        is_active = getattr(user, "is_active", None)
        return is_active or is_active is None
