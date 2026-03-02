from django.db import models

# Create your models here.
from django.db.models import CASCADE


class ClientRegister_Model(models.Model):
    username = models.CharField(max_length=30)
    email = models.EmailField(max_length=30)
    password = models.CharField(max_length=10)
    phoneno = models.CharField(max_length=10)
    country = models.CharField(max_length=30)
    state = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    gender= models.CharField(max_length=30)
    address= models.CharField(max_length=30)


class food_recommend_type(models.Model):

    Foodid= models.CharField(max_length=300)
    Userid= models.CharField(max_length=300)
    Following_Users= models.CharField(max_length=300)
    Followers= models.CharField(max_length=300)
    Rating= models.CharField(max_length=300)
    Time= models.CharField(max_length=300)
    Review= models.CharField(max_length=30000)
    Prediction= models.CharField(max_length=300)


class detection_accuracy(models.Model):

    names = models.CharField(max_length=300)
    ratio = models.CharField(max_length=300)

class detection_ratio(models.Model):

    names = models.CharField(max_length=300)
    ratio = models.CharField(max_length=300)



