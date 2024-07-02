from django.contrib.auth.models import User
from rest_framework import generics, permissions, renderers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .models import Snippet, APIAction
from .permissions import IsOwnerOrReadOnly, IsStaffOrReadOnly
from .serializers import SnippetSerializer, UserSerializer, UserCreateSerializer, APIActionSerializer


class SnippetHighlight(generics.GenericAPIView):
    queryset = Snippet.objects.all()
    renderer_classes = (renderers.StaticHTMLRenderer,)

    def get(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)


@api_view(["GET"])
def api_root(request, format=None):
    data = {
        "users": {
            "list": reverse("user-list", request=request, format=format),
        },
        "snippets": reverse("snippet-list", request=request, format=format),
    }

 # Only include "create" under "users" if user is staff
    if request.user.is_staff:
        data["users"]["create"] = reverse("user-create", request=request, format=format)

    # Only include "apiactions" if user is staff
    if request.user.is_staff:
        data["apiactions"] = reverse("api-action-list", request=request, format=format)


    return Response(data)


class SnippetList(generics.ListCreateAPIView):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)  

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class SnippetDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    )  


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CreateUserList(generics.CreateAPIView):
    queryset = User.objects.filter(is_staff=True)
    serializer_class = UserCreateSerializer  
    permission_classes = (permissions.IsAuthenticated,IsStaffOrReadOnly)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Save the serializer data to create a new user
            user = serializer.save()

            # Log the API action
            APIAction.log_action(request.user, User.__name__, user.id, 'create')

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class APIActionList(generics.ListAPIView):
    queryset = APIAction.objects.all()
    serializer_class = APIActionSerializer
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)