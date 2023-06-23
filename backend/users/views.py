from django.shortcuts import get_object_or_404
from .models import User, Subscribtion
from rest_framework.response import Response
from rest_framework import status, permissions, serializers
from .serializers import (SubscribtionSerializer,
                          CustomUserSerializer,
                          SubscriptionCreateSerializer)
# from django.http import HttpResponse
# from rest_framework.decorators import api_view, permission_classes
from .pagination import LimitPageNumerPagination
from djoser.views import UserViewSet
from rest_framework.decorators import action
# from rest_framework.pagination import PageNumberPagination
# from rest_framework.serializers import ListSerializer


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    pagination_class = LimitPageNumerPagination

    @action(
        methods=['get'], detail=False,
        serializer_class=SubscribtionSerializer
    )
    def subscriptions(self, request):
        user = self.request.user

        def queryset():
            return User.objects.filter(following__user=user)

        self.get_queryset = queryset
        return self.list(request)

    @action(
        methods=['post', 'delete'], detail=True,
        serializer_class=SubscribtionSerializer
    )
    def subscribe(self, request, id):
        user = self.request.user
        author = self.get_object()
        if request.method == 'DELETE':
            instance = user.follower.filter(author=author)
            if not instance:
                raise serializers.ValidationError(
                    {
                        'errors': [
                            'Вы не подписаны на этого автора.'
                        ]
                    }
                )
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        data = {
            'user': user.id,
            'author': id
        }
        subscription = SubscriptionCreateSerializer(data=data)
        subscription.is_valid(raise_exception=True)
        subscription.save()
        serializer = self.get_serializer(author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
