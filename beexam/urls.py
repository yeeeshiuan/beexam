from django.urls import include, path
from rest_framework import routers
from member import views as member_views
from main import views as main_views

router = routers.DefaultRouter()
router.register(r'users', member_views.UserViewSet, basename='users')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', main_views.index, name='index'),
    path(
        'activate/<uidb64>/<token>/',
        member_views.activate,
        name='activate'
    ),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
