# Generated by Django 4.2.5 on 2023-10-06 20:34

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_alter_user_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=50, verbose_name='имя'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, max_length=50, verbose_name='фамилия'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=50, unique=True, validators=[django.core.validators.RegexValidator(message='Имя пользователя содержит недопустимый символ', regex='^[\\w.@+-]+$')], verbose_name='Ник'),
        ),
    ]
