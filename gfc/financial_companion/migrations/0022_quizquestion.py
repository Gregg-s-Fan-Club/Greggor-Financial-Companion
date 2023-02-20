# Generated by Django 4.1.3 on 2023-02-12 11:25

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financial_companion', '0021_merge_20230210_1406'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuizQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=520, unique=True)),
                ('potential_answer_1', models.CharField(max_length=520)),
                ('potential_answer_2', models.CharField(max_length=520)),
                ('potential_answer_3', models.CharField(max_length=520)),
                ('potential_answer_4', models.CharField(max_length=520)),
                ('correct_answer', models.IntegerField(validators=[
                 django.core.validators.MaxValueValidator(4), django.core.validators.MinValueValidator(1)])),
                ('seeded', models.BooleanField()),
            ],
        ),
    ]