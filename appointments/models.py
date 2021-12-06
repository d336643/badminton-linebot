# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.postgres.fields import ArrayField



class Appointment(models.Model):
    step = models.IntegerField()
    starttime = models.DateTimeField(blank=True, null=True)
    endtime = models.DateTimeField(blank=True, null=True)
    hours = models.IntegerField(blank=True, null=True)
    user_order_ls = ArrayField(models.IntegerField(),blank=True, null=True)
    name = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        db_table = 'badminton"."appointment'


class HourDetail(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True, related_name='hour_details')
    court_cnt = models.IntegerField(blank=True, null=True)
    people_cnt = models.IntegerField(blank=True, null=True)
    hour = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'badminton"."hour_detail'

class User(models.Model):
    nickname = models.TextField(blank=True, null=True)  # This field type is a guess.
    role = models.TextField(blank=True, null=True)  # This field type is a guess.
    line_uid = models.TextField()  # This field type is a guess.
    avatar_url = models.TextField(blank=True, null=True)
    hourdetails = models.ManyToManyField(HourDetail, through='Invitation')

    class Meta:
        db_table = 'badminton"."user'

class Invitation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    hour_detail = models.ForeignKey(HourDetail, on_delete=models.CASCADE, null=True)
    status = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        db_table = 'badminton"."invitation'
