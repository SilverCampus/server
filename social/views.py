from rest_framework import viewsets
from .models import BoardPost, BoardComment, BoardPostLike
from .serializers import BoardPostSerializer, BoardCommentSerializer, BoardPostLikeSerializer

class BoardPostViewSet(viewsets.ModelViewSet):
    queryset = BoardPost.objects.all()
    serializer_class = BoardPostSerializer

class BoardCommentViewSet(viewsets.ModelViewSet):
    queryset = BoardComment.objects.all()
    serializer_class = BoardCommentSerializer

class BoardPostLikeViewSet(viewsets.ModelViewSet):
    queryset = BoardPostLike.objects.all()
    serializer_class = BoardPostLikeSerializer
