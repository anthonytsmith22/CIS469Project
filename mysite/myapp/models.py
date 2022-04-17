from django.db import models
import json

# Create your models here.

# Model for spending profile, holds users and entries contained in the spending profile
class SpendingProfile(models.Model):
    profile_name = models.CharField(max_length=30)
    data = models.JSONField()
    profile_owner = models.CharField(max_length=30)

# Model for spending entry containing entry date, name, description, amount, and owner
class Entry(models.Model):
    entry_date = models.DateField
    entry_name = models.CharField(max_length=20)
    entry_description = models.CharField(max_length=40)
    entry_amount = models.FloatField
    entry_owner = models.CharField(max_length=30)
