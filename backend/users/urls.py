from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

app_name = 'users'

router_v1 = DefaultRouter()
router_v1.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path(r'', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
