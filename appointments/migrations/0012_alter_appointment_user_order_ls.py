# Generated by Django 3.2.9 on 2021-12-05 19:43

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0011_alter_hourdetail_appointment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='user_order_ls',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), size=None),
        ),
    ]
