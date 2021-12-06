from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class Richmenu(models.Model):
    token = models.TextField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    role = models.TextField(blank=True, null=True)
    urls = ArrayField(models.TextField(),blank=True, null=True)
    class Meta:
        db_table = 'badminton"."richmenu'