from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, serializers, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly
                                        )

from api.permissions import IsOwnerOrReadOnly
from api.serializers import (CommentSerializer,
                             FollowSerializer,
                             GroupSerializer,
                             PostSerializer
                             )
from posts.models import Group, Post

User = get_user_model()


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)


class GroupViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        queryset = post.comments.all()
        return queryset

    def perform_create(self, serializer: serializers.Serializer):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        serializer.save(author=self.request.user, post=post)


class FollowViewSet(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ('following__username', 'user__username')

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.request.user.pk)
        queryset = user.follower.all()
        return queryset

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)
