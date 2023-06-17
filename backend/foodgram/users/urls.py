from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubListView, follow_author

app_name = 'users'

router_v1 = DefaultRouter()
router_v1.register(
    r'users/subscriptions',
    SubListView,
    basename='subscriptions',
)

urlpatterns = [
    path('users/<int:pk>/subscribe/',
         follow_author,
         name='follow-author'),
    path(r'', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
