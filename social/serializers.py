from rest_framework import serializers
from .models import BoardPost, BoardComment, BoardPostLike

class BoardPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardPost
        fields = '__all__'

class BoardCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardComment
        fields = '__all__'

class BoardPostLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardPostLike
        fields = '__all__'
