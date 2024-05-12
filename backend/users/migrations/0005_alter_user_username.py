# Generated by Django 4.2.11 on 2024-05-09 18:55

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_user_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=150, unique=True, validators=[django.core.validators.RegexValidator(message='Недопустимый символ в имени пользователя', regex='^[w.@+-]+Z')], verbose_name='Уникальный юзернейм'),
        ),
    ]