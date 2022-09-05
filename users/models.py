from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

# Create your models here.
class User(AbstractUser):
    username = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    name = models.CharField(max_length=100,null=True,blank=True)
    city = models.CharField(max_length=100,null=True,blank=True)
    state = models.CharField(max_length=50,null=True,blank=True)
    age = models.PositiveIntegerField(null=True,blank=True)
    gender = models.CharField(max_length=30,null=True,blank=True)
    is_verified = models.BooleanField(default=False)
    phoneNumberRegex = RegexValidator(regex = r"^\+?1?\d{8,15}$")
    phoneNumber = models.CharField(validators = [phoneNumberRegex], max_length = 16, unique = True,null=True,blank=True)
    registered_with_OTP = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        if not self.pk:
            self.username = str(self.email.split('@')[0])
        super(User, self).save(*args, **kwargs)

class PasswordReset(models.Model):
    email = models.CharField(max_length=255)
    otp = models.CharField(max_length=255, unique=True)
