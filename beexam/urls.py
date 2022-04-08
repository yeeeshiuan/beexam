from django.urls import include, path
from rest_framework import routers
from member import views as member_views
from main import views as main_views

router = routers.DefaultRouter()
router.register(r'users', member_views.UserViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', main_views.index, name='index'),
    path('dashboard/', main_views.dashboard, name='dashboard'),
    path('profile/', main_views.profile, name='profile'),
    path('privacy-policies/', main_views.privacy_policies, name="privacy_policies"),
    path(
        'activate/<uidb64>/<token>/',
        member_views.activate,
        name='activate'
    ),
    path('post-login/', member_views.post_login, name="login"),
    path('resend-activate-email/', member_views.resend_activate_email, name="resend_activate_email"),
    path('post-logout/', member_views.post_logout, name="logout"),
    path('fb-auth-callback/', member_views.fb_auth_callback, name="fb_auth_callback"),
    path('google-auth-callback/', member_views.google_auth_callback, name="google_auth_callback"),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
