from django.middleware.csrf import CsrfViewMiddleware
from django.conf import settings
import json

CSRF_SESSION_KEY = "_csrftoken"


class CustomCsrfMiddleware(CsrfViewMiddleware):

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if request.GET.get('state'):
            request.COOKIES[settings.CSRF_COOKIE_NAME] = request.GET.get('state')
            return super().process_view(request, callback, callback_args, callback_kwargs)
        else:
            return super().process_view(request, callback, callback_args, callback_kwargs)
