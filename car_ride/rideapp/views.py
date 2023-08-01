from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import authentication, permissions
from rest_framework.authentication import SessionAuthentication
from django.contrib.auth.models import User
import jwt, datetime
from rest_framework.exceptions import AuthenticationFailed
from .models import Driver, DriverLastLocUpdate, PriceSlab, BasePrice, CarRide, DriverLastLocUpdate
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer, RegisterSerializer, DriverSerializer, DriverLocationUpdateSerializer, PaymentSerializer, PaymentCalculateSerializer, BasePriceSerializer, RiderRequestSerializer, DriverLocationSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics
from django.contrib.auth import login, logout
# from rest_framework.authtoken.serializers import AuthTokenSerializer
# from knox.views import LoginView as KnoxLoginView
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

class LoginAPI(APIView):

	def post(self, request):
		email = request.data['username']
		password = request.data['password']

		user = User.objects.filter(email=email).first()

		if user is None:
			raise AuthenticationFailed('User not found!')

		if not user.check_password(password):
			raise AuthenticationFailed('Incorrect password!')

		payload = {
			'id': user.id,
			'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
			'iat': datetime.datetime.utcnow()
		}

		token = jwt.encode(payload, 'secret', algorithm='HS256').decode("utf-8")

		response = Response()

		response.set_cookie(key='jwt', value=token, httponly=True)
		response.data = {
			'jwt': token
		}
		return response

class LogoutAPI(APIView):

	def post(self, request):
		response = Response()
		response.delete_cookie('jwt')
		response.data = {
			'message': 'success'
		}
		return response

class UserView(APIView):

	def get(self, request):
		token = request.headers.get('Authorization')

		if not token or token == 'undefined':
			raise AuthenticationFailed('Unauthenticated!')

		try:
			payload = jwt.decode(token, 'secret', algorithm=['HS256'])
		except jwt.ExpiredSignatureError:
			raise AuthenticationFailed('Unauthenticated!')

		user = User.objects.filter(id=payload['id']).first()
		serializer = UserSerializer(user)
		return Response(serializer.data)

class DriverAPI(APIView):
	permission_classes = (AllowAny,)
	serializer_class = DriverSerializer

	def get_object(self, driver_id):
		try:
			return Driver.objects.get(driver_id=driver_id)
		except Driver.DoesNotExist:
			return None

	def get(self, request, id=None, *args, **kwargs):
		driver_id = request.GET.get('id', False)
		if not driver_id:
			driver = Driver.objects.all()
		else:
			driver = Driver.objects.filter(driver_id = driver_id)
		serializer = DriverSerializer(driver, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)

	def post(self, request, *args, **kwargs):
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
	permission_classes = (AllowAny),
	# authentication_classes = [authentication.TokenAuthentication]
	# permission_classes = [permissions.IsAuthenticated]
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
		service_provider = carrier.name_for_number(ph_no, "en")
		key = "38372d4eb0584cb6b90bbf1ee231d2f4"
		geo = OpenCageGeocode(key);
		query = str(your_loc)
		result = geo.geocode(query)
		lat = result[0]['geometry']['lat']
		lng = result[0]['geometry']['lng']
		return HttpResponse(ip_detail)


	def post(self, request, *args, **kwargs):
		print("--------------ffffffpost---------------");
		print(request.data);
		data = {
			# 'driver_update_id': 1,
			'driver_id': request.data.get('driver_id'),
			'longitude': request.data.get('longitude'),
			'latitude': request.data.get('latitude')
		}

		# last_update = DriverLastLocUpdate.objects.filter(driver_id=1)
		last_update = DriverLastLocUpdate.objects.filter(driver_id = request.data.get('driver_id')).first();
		print(last_update);
		if last_update:
			serializer = DriverLocationUpdateSerializer(instance=last_update, data = data, partial=True)
			if serializer.is_valid():
				serializer.save()
				return Response(serializer.data, status=status.HTTP_200_OK)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		serializer = DriverLocationUpdateSerializer(data = data)
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


class PaymentCalculateAPI(APIView):
	serializer_class = PaymentCalculateSerializer

	def post(self, request, *args, **kwargs):
		print(request.data);
		data = {
			'total_km': request.data.get('total_km')
		}
		price_slab = PriceSlab.objects.filter(from_km__lte = float(request.data.get('total_km')), to_km__gte = float(request.data.get('total_km'))).first()
		total_price = 0
		if price_slab:
			price = price_slab.price_per_km
			total_price_cents = float(request.data.get('total_km')) * float(price)
			total_price = round((total_price_cents / 100),2);
			print(total_price);
		serializer = PaymentCalculateSerializer(data = data)
		response = Response()
		if request.data.get('total_km'):
			response.data = {
				'message': 'success',
				'total_price': total_price
			}
			return response
		return Response({"Distance can't be fetched"}, status=status.HTTP_400_BAD_REQUEST)

class BasePriceViewSet(APIView):
	permission_classes = (AllowAny,)

	def get(self, request, *args, **kwargs):
		objs = BasePrice.objects.all()
		data = BasePriceSerializer(objs, many=True).data
		return Response(data, status=status.HTTP_200_OK)

class RiderRequestAPI(APIView):
	permission_classes = (AllowAny),
	serializer_class = RiderRequestSerializer

	def post(self, request, *args, **kwargs):
		# print("---------hell0-----------");
		print(request.data);
		user = None;
		if request.data.get('jwt'):
			payload = jwt.decode(request.data.get('jwt'), 'secret', algorithm=['HS256'])
			user = User.objects.filter(id=payload['id']).first()
			print(user);
			print(user.id);
			if not user:
				print("---------hell02222-----------");
				return Response({"User not found"}, status=status.HTTP_400_BAD_REQUEST)
			print("---------hell0111-----------");
		data = {
			'from_loc': request.data.get('pickup'),
			'to_loc': request.data.get('dropoff'),
			'price': request.data.get('amount'),
			'pay_type': request.data.get('pay_type'),
			'state': request.data.get('state'),
			'user_id': user.id,
		}
		print(data);
		serializer = RiderRequestSerializer(data = data)
		print("-fffffffffffffffffff");
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def put(self, request, *args, **kwargs):
		print("------------put");
		print(request.data)
		rider_id = request.data.get('ride_id', False)
		rider_obj = CarRide.objects.get(ride_id=rider_id)
		if not rider_obj:
			return Response({"res": "Object with rider id does not exist"}, status=status.HTTP_400_BAD_REQUEST)
		data = {
			'ride_id': request.data.get('ride_id'),
			'from_loc': request.data.get('pickup'),
			'to_loc': request.data.get('dropoff'),
			'price': request.data.get('amount'),
			'pay_type': request.data.get('pay_type'),
			'state': request.data.get('state'),
			'user_id': request.data.get('username'),
			'driver_id': request.data.get('driver_id')
		}
		serializer = RiderRequestSerializer(instance=rider_obj, data = data, partial=True)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


	# def get(self, request, *args, **kwargs):
	# 	ride_request = CarRide.objects.all()
	# 	# ride_request = CarRide.objects.filter(state = "draft")
	# 	serializer = RiderRequestSerializer(ride_request, many=True)
	# 	return Response(serializer.data, status=status.HTTP_200_OK)

	def get(self, request, id=None, *args, **kwargs):
		ride_request_id = request.GET.get('id', False)
		if not ride_request_id:
			ride_request = CarRide.objects.all();
		else:
			ride_request = CarRide.objects.filter(ride_id = ride_request_id)
		serializer = RiderRequestSerializer(ride_request, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)

class DriverLastLocationAPI(APIView):
	permission_classes = (AllowAny),


	def get(self, request, id=None, *args, **kwargs):
		print("gggggggggggggggggg");
		driver_loc_id = request.GET.get('id', False)
		print(driver_loc_id);
		if not driver_loc_id:
			driver_loc = DriverLastLocUpdate.objects.all();
		else:
			driver_loc = DriverLastLocUpdate.objects.filter(driver_id = driver_loc_id)
			print(driver_loc);
		serializer = DriverLocationSerializer(driver_loc, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)