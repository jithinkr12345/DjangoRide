from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import authentication, permissions
from django.contrib.auth.models import User
from .models import Driver, DriverLastLocUpdate
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer, RegisterSerializer, DriverSerializer, DriverLocationUpdateSerializer, PaymentSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics
from django.contrib.auth import login
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.views import LoginView as KnoxLoginView
import requests
import phonenumbers
from phonenumbers import geocoder, carrier
from opencage.geocoder import OpenCageGeocode
import folium

from plyer import gps
from django.core.mail import send_mail
from django.conf import settings

api_key = '93efe7db09584d8d842ccbdcaa4aca00'
api_url = 'https://ipgeolocation.abstractapi.com/v1/?api_key=' + api_key


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

class RiderMapAPI(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DriverLocationUpdateSerializer

    def get_ip_location_details(self, request):
        ip = self.get_my_ip(request)
        response = requests.get(api_url + "&ip_address=" + ip)
        return response.content

    def get_my_ip(self, request):
        x_forwaded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwaded_for:
            ip = x_forwaded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        # ip_address = "208.98.222.69"
        ip = "184.144.61.211"
        return ip
        

    def get(self, request, *args, **kwargs):
        # return Response({"res": "Rider Map!"}, status=status.HTTP_200_OK)
        ip_detail = self.get_ip_location_details(request)


        # ph_no = "+12265036509"
        ph_no = "+918281756866"
        ph_no = phonenumbers.parse(ph_no)
        your_loc = geocoder.description_for_number(ph_no, "en")
        print(your_loc);
        service_provider = carrier.name_for_number(ph_no, "en")
        print(carrier.name_for_number(ph_no, "en"));
        key = "38372d4eb0584cb6b90bbf1ee231d2f4"
        geo = OpenCageGeocode(key);
        query = str(your_loc)
        result = geo.geocode(query)
        # print(result)
        lat = result[0]['geometry']['lat']
        lng = result[0]['geometry']['lng']
        print(lat)
        print(lng)
        return HttpResponse(ip_detail)


    def post(self, request, *args, **kwargs):
        print(request.data)
        data = {
            'driver_update_id': 1,
            'driver_id': 1,
            'longitude': request.data.get('longitude'),
            'latitude': request.data.get('latitude')
        }
        # last_update = DriverLastLocUpdate.objects.filter(driver_id=1)
        last_update = DriverLastLocUpdate.objects.get(driver_update_id=1)
        if last_update:
            serializer = DriverLocationUpdateSerializer(instance=last_update, data = data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        print(data)
        serializer = DriverLocationUpdateSerializer(data = data)
        print(serializer.is_valid)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailAPI(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):

        send_mail(subject='Payment Info for Ride 001234', message='Ride form Kitchener to London have been successfully completed', from_email=settings.EMAIL_HOST_USER, recipient_list=["krjithin520@gmail.com"])
        return Response({"res": "Mail Send Successfully"}, status=status.HTTP_200_OK)

class PaymentAPI(APIView):
    permission_classes = (AllowAny,)
    serializer_class = PaymentSerializer

    def post(self, request, *args, **kwargs):
        print(request.data)
        data = {
            'payment_id': request.data.get('payment_id'),
            'invoice_id': request.data.get('invoice_id'),
            'transaction_id': request.data.get('transaction_id'),
            'mode_of_pay': request.data.get('mode_of_pay'),
            'price': request.data.get('price'),
            # 'email': request.data.get('email'),
            # 'phone': request.data.get('phone'),
            # 'license_no': request.data.get('license_no'),
            # 'car_year': request.data.get('car_year'),
            # 'car_model': request.data.get('car_model'),
            # 'car_name': request.data.get('car_name'),
            # 'car_no': request.data.get('car_no'),
            'create_date': request.data.get('create_date'),
            'write_date': request.data.get('write_date'),
        }
        serializer = PaymentSerializer(data = data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)