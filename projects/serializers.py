from .models import Project, Comment
from rest_framework import serializers

class CommentSerializer(serializers.ModelSerializer):
    text = serializers.CharField(max_length=500, required=True)

    class Meta:
        model = Comment
        fields = ['text']