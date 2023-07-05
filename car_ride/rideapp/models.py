from django.db import models
import datetime
from django.utils import timezone
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

# class User(models.Model):
# 	user_id = models.IntegerField(primary_key=True)
# 	first_name = models.CharField(max_length=100)
# 	last_name = models.CharField(max_length=100)
# 	age = models.IntegerField()
# 	dob = models.CharField(max_length=100)
# 	email = models.CharField(max_length=100)
# 	phone = models.CharField(max_length=100)
# 	senior_citizen = models.BooleanField()
# 	id_proof = models.ImageField()
# 	is_pass = models.BooleanField()
# 	pass_from_date = models.DateTimeField()
# 	pass_to_date = models.DateTimeField()
# 	create_date = models.DateTimeField(default=timezone.now)
# 	write_date = models.DateTimeField(auto_now=True)



@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class Driver(models.Model):
	
	driver_id = models.IntegerField(primary_key=True)
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	age = models.IntegerField()
	dob = models.CharField(max_length=100)
	email = models.CharField(max_length=100)
	phone = models.CharField(max_length=100)
	license_no = models.CharField(max_length=100)
	car_year = models.IntegerField()
	car_model = models.CharField()
	car_name = models.CharField(max_length=100)
	car_no = models.CharField(max_length=100)
	create_date = models.DateTimeField(default=timezone.now)
	write_date = models.DateTimeField(auto_now=True)
	# create_id = models.ForeignKey(auth_user, on_delete=models.CASCADE)
	# write_id = models.ForeignKey(auth_user, on_delete=models.CASCADE)

class DriverLocations(models.Model):

	driver_loc_id = models.IntegerField(primary_key=True)
	driver_id = models.ForeignKey(Driver, on_delete=models.CASCADE)
	locations = models.CharField(max_length=100)
	create_date = models.DateTimeField(default=timezone.now)
	write_date = models.DateTimeField(auto_now=True)

class DriverLastLocUpdate(models.Model):
	driver_update_id = models.IntegerField(primary_key=True)
	driver_id = models.ForeignKey(Driver, on_delete=models.CASCADE)
	longitude = models.CharField(max_length=100)
	latitude = models.CharField(max_length=100)

class CarAmenities(models.Model):

	amenities_id = models.IntegerField(primary_key=True)
	driver_id = models.ForeignKey(Driver, on_delete=models.CASCADE)
	features = models.CharField(max_length=100)
	create_date = models.DateTimeField(default=timezone.now)
	write_date = models.DateTimeField(auto_now=True)

class CarRide(models.Model):

	ride_id = models.IntegerField(primary_key=True)
	# user_id = models.ForeignKey(AnonymousUser, on_delete=models.CASCADE)
	driver_id = models.ForeignKey(Driver, on_delete=models.CASCADE)
	from_loc = models.CharField(max_length=100)
	to_loc = models.CharField(max_length=100)
	price = models.DecimalField(max_digits=6, decimal_places=2)
	pay_type = models.CharField(max_length=100)
	create_date = models.DateTimeField(default=timezone.now)
	write_date = models.DateTimeField(auto_now=True)

class CarPool(models.Model):

	pool_id = models.IntegerField(primary_key=True)
	# user_id = models.ForeignKey(AnonymousUser, on_delete=models.CASCADE)
	driver_id = models.ForeignKey(Driver, on_delete=models.CASCADE)
	from_loc = models.CharField(max_length=100)
	to_loc = models.CharField(max_length=100)
	price = models.DecimalField(max_digits=6, decimal_places=2)
	available_seats = models.IntegerField()
	create_date = models.DateTimeField(default=timezone.now)
	write_date = models.DateTimeField(auto_now=True)

class Invoice(models.Model):

	invoice_id = models.IntegerField(primary_key=True)
	ride_id = models.ForeignKey(CarRide, on_delete=models.CASCADE)
	pool_id = models.ForeignKey(CarPool, on_delete=models.CASCADE)
	# user_id = models.ForeignKey(AnonymousUser, on_delete=models.CASCADE)
	driver_id = models.ForeignKey(Driver, on_delete=models.CASCADE)
	total_payment = models.DecimalField(max_digits=6, decimal_places=2)
	pay_type = models.CharField(max_length=100)
	create_date = models.DateTimeField(default=timezone.now)
	write_date = models.DateTimeField(auto_now=True)

class Payment(models.Model):

	payment_id = models.IntegerField(primary_key=True)
	invoice_id = models.ForeignKey(Invoice, on_delete=models.CASCADE)
	# user_id = models.ForeignKey(User, on_delete=models.CASCADE)
	transaction_id = models.CharField(max_length=100)
	mode_of_pay = models.CharField(max_length=100)
	price = models.DecimalField(max_digits=6, decimal_places=2)
	create_date = models.DateTimeField(default=timezone.now)
	write_date = models.DateTimeField(auto_now=True)