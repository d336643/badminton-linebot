# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Appointment(models.Model):
    uid = models.IntegerField(primary_key=True)
    step = models.IntegerField()
    starttime = models.TimeField(blank=True, null=True)
    endtime = models.TimeField(blank=True, null=True)
    user_order_ls = models.TextField(blank=True, null=True)  # This field type is a guess.
    name = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        db_table = 'badminton"."appointment'


class HourDetail(models.Model):
    uid = models.IntegerField(primary_key=True)
    appointment_id = models.IntegerField(blank=True, null=True)
    court_cnt = models.IntegerField(blank=True, null=True)
    people_cnt = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'badminton"."hour_detail'


class Invitation(models.Model):
    uid = models.IntegerField(primary_key=True)
    user_id = models.IntegerField(blank=True, null=True)
    hour_detail_id = models.IntegerField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        db_table = 'badminton"."invitation'


class User(models.Model):
    uid = models.IntegerField(primary_key=True)
    nickname = models.TextField(blank=True, null=True)  # This field type is a guess.
    role = models.TextField(blank=True, null=True)  # This field type is a guess.
    line_uid = models.TextField()  # This field type is a guess.
    avatar_url = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'badminton"."user'
