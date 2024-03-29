# Generated by Django 4.0.4 on 2022-04-16 22:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entry_name', models.CharField(max_length=20)),
                ('entry_description', models.CharField(max_length=40)),
                ('entry_owner', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='SpendingProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_name', models.CharField(max_length=30)),
                ('data', models.JSONField()),
                ('profile_owner', models.CharField(max_length=30)),
            ],
        ),
    ]
