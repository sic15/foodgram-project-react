# Generated by Django 4.2.5 on 2023-09-16 16:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('measure', models.CharField(choices=[('g', 'г'), ('kg', 'кг'), ('l', 'л'), ('ml', 'мл'), ('piece', 'шт')], max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='Quantity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('slug', models.SlugField(max_length=200, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('cooking_time', models.IntegerField()),
                ('image', models.ImageField(blank=True, upload_to='recipes/', verbose_name='Картинка')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe', to=settings.AUTH_USER_MODEL)),
                ('ingredients', models.ManyToManyField(through='food.Quantity', to='food.ingredient')),
                ('tag', models.ManyToManyField(related_name='recipe', to='food.tag')),
            ],
        ),
        migrations.AddField(
            model_name='quantity',
            name='ingredient',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='food.recipe'),
        ),
        migrations.AddField(
            model_name='quantity',
            name='measure',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='food.ingredient'),
        ),
    ]
