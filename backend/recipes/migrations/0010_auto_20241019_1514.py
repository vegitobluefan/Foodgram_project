# Generated by Django 3.2.6 on 2024-10-19 12:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0009_auto_20241018_1803'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='groups',
        ),
        migrations.RemoveField(
            model_name='user',
            name='user_permissions',
        ),
        migrations.DeleteModel(
            name='SubscriptionUser',
        ),
        migrations.DeleteModel(
            name='User',
        ),
    ]