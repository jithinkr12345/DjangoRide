from django.contrib.auth.models import User
from .models import Driver, DriverLastLocUpdate, Payment, CarRide
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

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')
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
        return user


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ["driver_id", "first_name", "last_name", "age", "dob", "email", "phone", "license_no", "car_year",
                  "car_model", "car_name", "car_no", "create_date", "write_date"]


class DriverLocationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverLastLocUpdate
        fields = ["driver_update_id", "driver_id", "longitude", "latitude"]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["payment_id", "invoice_id", "transaction_id", "mode_of_pay", "price", "create_date", "write_date"]


class CarRideSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarRide
        fields = "__all__"
