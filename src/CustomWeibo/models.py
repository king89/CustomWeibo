# -*- coding:utf-8 -*-

from django.db import models

class Users(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=100)
    image_url = models.CharField(max_length=1000)
    statuses_count = models.PositiveIntegerField()
    friends_count = models.PositiveIntegerField()
    followers_count = models.PositiveIntegerField()
    verified = models.BooleanField()
    verified_type = models.IntegerField()
    auth_token = models.CharField(max_length=200)
    expired_time = models.FloatField()


