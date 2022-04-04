from django.middleware.csrf import CsrfViewMiddleware
import json

CSRF_SESSION_KEY = "_csrftoken"


class CustomCsrfMiddleware(CsrfViewMiddleware):

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if request.GET.get('state'):
            print(request.GET.get('state'))
            state = json.loads(request.GET.get('state'))
            request.session[CSRF_SESSION_KEY] = state.csrf
            return super().process_view(request, callback, callback_args, callback_kwargs)
        else:
            return super().process_view(request, callback, callback_args, callback_kwargs)
