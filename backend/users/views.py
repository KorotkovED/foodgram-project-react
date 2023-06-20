from django.shortcuts import get_object_or_404
from .models import User, Subscribtion
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from .serializers import SubscribtionSerializer
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from .pagination import LimitPageNumerPagination


@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def follow_author(request, pk):
    """Функция подписки пользователя на автора."""
    user = get_object_or_404(User, username=request.user.username)
    author = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        if user.id == author.id:
            content = {'errors': 'Нельзя подписываться на себя'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        if Subscribtion.objects.filter(user=user, author=author).exists():
            content = {'errors': 'Вы уже подписаны на этого автора!'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            Subscribtion.objects.create(user=user, author=author)
            follower = User.objects.all().filter(username=author)
            serializer = SubscribtionSerializer(follower, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    if request.method == 'DELETE':
        sub = Subscribtion.objects.get(user=user, author=author)
        if sub is None:
            content = {'errors': 'Вы не подписаны на данного автора!'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        sub.delete()
        return HttpResponse('Вы отписались от автора!',
                            status=status.HTTP_204_NO_CONTENT)


class SubListView(viewsets.ReadOnlyModelViewSet):
    """Класс для генерации списка подписок пользователя."""

    queryset = User.objects.all()
    serializer_class = SubscribtionSerializer
    pagination_class = LimitPageNumerPagination
    permission_classes = (permissions.IsAuthenticated,)
    search_fields = ('^following__user')

    def get_queryset(self):
        user = self.request.user
        new_queryset = User.objects.filter(following__user=user)
        return new_queryset
