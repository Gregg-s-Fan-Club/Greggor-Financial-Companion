# Generated by Django 4.1.3 on 2023-03-20 14:53

from django.db import migrations, models
import financial_companion.models.transaction_models


class Migration(migrations.Migration):

    dependencies = [
        ('financial_companion', '0034_alter_recurringtransaction_receiver_account_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recurringtransaction',
            name='image',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='image',
        ),
        migrations.AddField(
            model_name='recurringtransaction',
            name='file',
            field=models.FileField(blank=True, upload_to=financial_companion.models.transaction_models.change_filename),
        ),
        migrations.AddField(
            model_name='transaction',
            name='file',
            field=models.FileField(blank=True, upload_to=financial_companion.models.transaction_models.change_filename),
        ),
    ]
