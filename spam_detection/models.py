from django.db import models
from django.contrib.auth.models import User

# Create your models here.

#User Model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    blacklisted_senders = models.ManyToManyField('BlacklistedSender', blank=True)
    whitelisted_senders = models.ManyToManyField('WhitelistedSender', blank=True)

#Blacklist Model
class BlacklistedSender(models.Model):
    email = models.EmailField(unique=True)

#Whitelist Model
class WhitelistedSender(models.Model):
    email = models.EmailField(unique=True)

