# Generated by Django 3.2.3 on 2024-10-18 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_alter_user_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_subscribed',
        ),
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, help_text='Добавьте ваш аватар', upload_to='user_avatars', verbose_name='Аватар'),
        ),
    ]
