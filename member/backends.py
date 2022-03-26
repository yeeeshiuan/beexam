from django.contrib.auth.backends import BaseBackend
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from beexam.utils import account_activation_token  
from member.models import User


class ActivateBackend(BaseBackend):
    def authenticate(self, request, uidb64=None, email=None, token=None, **kwargs):
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
