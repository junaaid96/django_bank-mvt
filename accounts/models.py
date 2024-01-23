from django.db import models
from django.contrib.auth.models import User
from .constants import ACCOUNT_TYPE, GENDER_TYPE

# Create your models here.


class UserBankAccount(models.Model):
    # django has built in user model. now i create my own user model with other fields and make a OneToOne relationship with the built in user model. i use related_name to access built in user model from my user model. on_delete=models.CASCADE means if the built in user model is deleted, my user model will also be deleted.

    user = models.OneToOneField(
        User, related_name='account', on_delete=models.CASCADE)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE)
    account_no = models.IntegerField(unique=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_TYPE)
    balance = models.DecimalField(default=0, max_digits=12, decimal_places=2)
    initial_deposit_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.account_no} - {self.user.username} - {self.account_type}"


class UserAddress(models.Model):
    user = models.OneToOneField(
        User, related_name='address', on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    postal_code = models.IntegerField()
    
    def __str__(self):
        return f"{self.user.username} - {self.street_address} - {self.city} - {self.postal_code}"
    