from django.contrib.auth.models import User
from .models import Driver, DriverLastLocUpdate, Payment, CustomUser, PriceSlab, BasePrice, CarRide, DriverLastLocUpdate
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = User
		fields = ['id', 'username', 'email', 'first_name', 'last_name']

class RegisterSerializer(serializers.ModelSerializer):
	email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
	password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
	password2 = serializers.CharField(write_only=True, required=True)
	user_type = serializers.CharField(write_only=True, required=True)

	class Meta:
		model = User
		fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name', 'user_type')
		extra_kwargs = {
	  		'first_name': {'required': True},
	  		'last_name': {'required': True}
		}
	def validate(self, attrs):
		if attrs['password'] != attrs['password2']:
		  raise serializers.ValidationError(
			{"password": "Password fields didn't match."})
		return attrs
	def create(self, validated_data):
		user = User.objects.create(
			username=validated_data['username'],
			email=validated_data['email'],
			first_name=validated_data['first_name'],
			last_name=validated_data['last_name']
		)
		user.set_password(validated_data['password'])
		user.save()
		user_type = CustomUser.objects.create(
			# user_id=user.id,
			user=user,
			user_type=validated_data['user_type']
			)
		return user

class DriverSerializer(serializers.ModelSerializer):
	class Meta:
		model = Driver
		fields = ["driver_id","first_name","last_name","age","dob","email","phone","license_no","car_year","car_model","car_name","car_no","create_date","write_date"]

class DriverLocationUpdateSerializer(serializers.ModelSerializer):
	class Meta:
		model = DriverLastLocUpdate
		fields = "__all__"

class PaymentSerializer(serializers.ModelSerializer):
	class Meta:
		model = Payment
		fields = ["payment_id","invoice_id","transaction_id","mode_of_pay","price","create_date","write_date"]


class PaymentCalculateSerializer(serializers.ModelSerializer):
	class Meta:
		model = PriceSlab
		fields = ["slab_id","from_km","to_km","price_per_km"]


class BasePriceSerializer(serializers.ModelSerializer):
	class Meta:
		model = BasePrice
		fields = "__all__"

class RiderRequestSerializer(serializers.ModelSerializer):
	class Meta:
		model = CarRide
		fields = "__all__"

class DriverLocationSerializer(serializers.ModelSerializer):
	class Meta:
		model = DriverLastLocUpdate
		fields = "__all__"
