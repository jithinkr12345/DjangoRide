from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import authentication, permissions
from django.contrib.auth.models import User
from .models import Driver
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer, RegisterSerializer, DriverSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics
from django.contrib.auth import login
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.views import LoginView as KnoxLoginView



class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

class ListUsers(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        usernames = [user.username for user in User.objects.all()]
        return Response(usernames)


class RegisterUserAPIView(generics.CreateAPIView):
	permission_classes = (AllowAny,)
	serializer_class = RegisterSerializer

class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginAPI, self).post(request, format=None)

class DriverAPI(APIView):
    permission_classes = (AllowAny,)
    serializer_class = DriverSerializer

    def get_object(self, driver_id):
        try:
            return Driver.objects.get(driver_id=driver_id)
        except Driver.DoesNotExist:
            return None

    def get(self, request, id=None, *args, **kwargs):
        print(request.GET.get('id', False))
        driver_id = request.GET.get('id', False)
        if not driver_id:
            driver = Driver.objects.all()
        else:
            driver = Driver.objects.filter(driver_id = driver_id)
        serializer = DriverSerializer(driver, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        print(request.data)
        data = {
            'driver_id': request.data.get('driver_id'),
            'first_name': request.data.get('f_name'),
            'last_name': request.data.get('l_name'),
            'age': request.data.get('age'),
            'dob': request.data.get('dob'),
            'email': request.data.get('email'),
            'phone': request.data.get('phone'),
            'license_no': request.data.get('license_no'),
            'car_year': request.data.get('car_year'),
            'car_model': request.data.get('car_model'),
            'car_name': request.data.get('car_name'),
            'car_no': request.data.get('car_no'),
            'create_date': request.data.get('create_date'),
            'write_date': request.data.get('write_date'),
        }
        serializer = DriverSerializer(data = data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        print(request.GET.get('id', False))
        driver_id = request.GET.get('id', False)
        driver_instance = self.get_object(driver_id)
        if not driver_instance:
            return Response({"res": "Object with driver id does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        data = {
            'driver_id': request.data.get('driver_id'),
            'first_name': request.data.get('f_name'),
            'last_name': request.data.get('l_name'),
            'age': request.data.get('age'),
            'dob': request.data.get('dob'),
            'email': request.data.get('email'),
            'phone': request.data.get('phone'),
            'license_no': request.data.get('license_no'),
            'car_year': request.data.get('car_year'),
            'car_model': request.data.get('car_model'),
            'car_name': request.data.get('car_name'),
            'car_no': request.data.get('car_no'),
            'create_date': request.data.get('create_date'),
            'write_date': request.data.get('write_date'),
        }
        serializer = DriverSerializer(instance=driver_instance, data = data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        driver_id = request.GET.get('id', False)
        driver_instance = self.get_object(driver_id)

        if not driver_instance:
            return Response({"res": "Object with driver id does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        driver_instance.delete()
        return Response({"res": "Driver Deleted!"}, status=status.HTTP_200_OK)