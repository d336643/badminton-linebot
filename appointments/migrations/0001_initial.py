# Generated by Django 3.2.9 on 2021-12-03 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('uid', models.BigIntegerField(primary_key=True, serialize=False)),
                ('step', models.IntegerField()),
                ('starttime', models.TimeField(blank=True, null=True)),
                ('endtime', models.TimeField(blank=True, null=True)),
                ('user_order_ls', models.TextField(blank=True, null=True)),
                ('name', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'badminton"."appointment',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='HourDetail',
            fields=[
                ('uid', models.BigIntegerField(primary_key=True, serialize=False)),
                ('appointment_id', models.BigIntegerField(blank=True, null=True)),
                ('court_cnt', models.IntegerField(blank=True, null=True)),
                ('people_cnt', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'badminton"."hour_detail',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('uid', models.BigIntegerField(primary_key=True, serialize=False)),
                ('user_id', models.BigIntegerField(blank=True, null=True)),
                ('hour_detail_id', models.BigIntegerField(blank=True, null=True)),
                ('status', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'badminton"."invitation',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('uid', models.BigIntegerField(primary_key=True, serialize=False)),
                ('nickname', models.TextField(blank=True, null=True)),
                ('role', models.TextField(blank=True, null=True)),
                ('line_uid', models.TextField()),
                ('avatar_url', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'badminton"."user',
                'managed': False,
            },
        ),
    ]
