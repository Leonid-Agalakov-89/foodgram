# Generated by Django 4.2.11 on 2024-05-18 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0009_shortlink_alter_ingredient_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shortlink',
            name='short_link',
            field=models.CharField(max_length=32, unique=True, verbose_name='Короткая ссылка рецепта'),
        ),
    ]