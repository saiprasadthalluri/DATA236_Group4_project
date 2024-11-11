# from rest_framework import generics
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.views import APIView
# from .api.serializers import UserModelSerializer
# from django.contrib.auth import authenticate
# from rest_framework_simplejwt.tokens import RefreshToken
# from taxi.tokens.custom_token import MyTokenObtainPairView, MyTokenObtainPairSerializer
# from rest_framework import status, permissions
# from rest_framework.response import Response
# from django.contrib.auth import get_user_model

# User = get_user_model()



# class CreateUserAPIVIEW(generics.CreateAPIView):
#     serializer_class = UserModelSerializer
#     permission_classes = [ permissions.AllowAny ]
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         refresh = ""
#         access_token = ""
#         try:
#             email = request.data.get("email")
#             user_pwd = request.data.get("password")
            
#             # # Authenticate user
#             user = authenticate(email=email, password=user_pwd)
#             # Generate tokens
#             if user:
#                 token_view = MyTokenObtainPairSerializer()
#                 refresh = token_view.get_token(user)
#                 access_token = refresh.access_token
#         except:
#             print("error happened")
            
#         response_data = {
#             "data": serializer.data,
#             "refresh": str(refresh),
#             "access": str(access_token)
#         }
#         return Response(response_data, status=status.HTTP_201_CREATED)




# class RetrieveUserAPI(generics.RetrieveUpdateAPIView):
#     serializer_class = UserModelSerializer
#     permission_classes = [ IsAuthenticated ]
#     queryset = User
#     def update(self, request, *args, **kwargs):
#         partial = kwargs.pop("partial", True)
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=partial)
#         serializer.is_valid(raise_exception=True)
#         self.perform_update(serializer)
#         return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    


from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from authapp.api.serializers import UserModelSerializer
from django.views.decorators.cache import cache_page

User = get_user_model()

class CreateUserAPIVIEW(generics.CreateAPIView):
    serializer_class = UserModelSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Authenticate user and generate tokens
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(email=email, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            response_data = {
                "user": serializer.data,
                "refresh": str(refresh),
                "access": str(access),
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response({"error": "Authentication failed."}, status=status.HTTP_401_UNAUTHORIZED)


class RetrieveUserAPI(generics.RetrieveUpdateAPIView):
    serializer_class = UserModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
