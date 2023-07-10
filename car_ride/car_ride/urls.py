"""
URL configuration for car_ride project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rideapp.views import ListUsers, CustomAuthToken, RegisterUserAPIView, LoginAPI, DriverAPI, RiderMapAPI, EmailAPI, PaymentAPI

urlpatterns = [
    path('api/token/auth', CustomAuthToken.as_view()),
    path('api/users/', ListUsers.as_view()),
    path('api/users/register', RegisterUserAPIView.as_view()),
    path('api/users/login', LoginAPI.as_view(), name='login'),
    path('admin/', admin.site.urls),
    path('api/drivers/', DriverAPI.as_view()),
    path('api/rider/map', RiderMapAPI.as_view()),
    path('api/rider/email', EmailAPI.as_view()),
    path('api/rider/payment', PaymentAPI.as_view())
]
