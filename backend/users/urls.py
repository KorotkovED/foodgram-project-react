from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

app_name = 'users'

router_v1 = DefaultRouter()
# router_v1.register(
#     r'users/subscriptions',
#     SubListView,
#     basename='subscriptions',
# )
router_v1.register(r'users', UserViewSet, basename='users')

# subscriptions = UserViewSet.as_view({'get': 'subscriptions', })

urlpatterns = [
    # path('users/<int:pk>/subscribe/',
    #      follow_author,
    #      name='follow-author'),
    # path('users/subscriptions/', subscriptions, name='subscriptions'),
    path(r'', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
