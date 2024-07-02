from django.contrib.auth.models import User
from rest_framework import serializers
from snippets.models import Snippet, LANGUAGE_CHOICES, STYLE_CHOICES
from .models import APIAction


class SnippetSerializer(serializers.HyperlinkedModelSerializer): 
    owner = serializers.ReadOnlyField(source="owner.username")
    highlight = serializers.HyperlinkedIdentityField(  
        view_name="snippet-highlight", format="html"
    )

    class Meta:
        model = Snippet
        fields = (
            "url",
            "id",
            "highlight",
            "title",
            "code",
            "linenos",
            "language",
            "style",
            "owner",
        )  


# Serializer for output (GET) operations
class UserSerializer(serializers.HyperlinkedModelSerializer):
    snippets = serializers.HyperlinkedRelatedField(
        many=True, view_name='snippet-detail', read_only=True
    )

    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'email', 'is_staff', 'snippets')


# Serializer for input (POST) operations
class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'is_staff')  # Example fields, adjust as per your model
        extra_kwargs = {
            'password': {'write_only': True},  # Ensures password is not included in GET responses
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user



class APIActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIAction
        fields = '__all__'