from django.db import models
import json

# Create your models here.

# Model for user Account including name, username, and password
class Account(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    user_name = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    password = models.CharField(max_length=30)

# Model for user profile, not containing password, for recognizing users in a spending profile
class UserProfile(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    user_name = models.CharField(max_length=30)
    associated_account = models.OneToOneField(Account, on_delete=models.CASCADE)

# Model for spending profile, holds users and entries contained in the spending profile
class SpendingProfile(models.Model):
    users = models.JSONField
    entries = models.JSONField

# Model for spending entry containing entry date, name, description, amount, and owner
class Entry(models.Model):
    entry_date = models.DateField
    entry_name = models.CharField(max_length=20)
    entry_description = models.CharField(max_length=40)
    entry_amount = models.FloatField
    entry_owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
