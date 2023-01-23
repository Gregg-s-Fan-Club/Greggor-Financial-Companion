# Generated by Django 4.1.3 on 2023-01-23 21:56

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import encrypted_fields.fields
import financial_companion.models.accounts_model


class Migration(migrations.Migration):

    dependencies = [
        ('financial_companion', '0012_accounttarget'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('potaccount_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='financial_companion.potaccount')),
                ('bank_name', models.CharField(max_length=50)),
                ('account_number', encrypted_fields.fields.EncryptedCharField(max_length=8, validators=[financial_companion.models.accounts_model.only_int, django.core.validators.MinLengthValidator(8, 'Account number must be 8 digits long')])),
                ('sort_code', encrypted_fields.fields.EncryptedCharField(max_length=6, validators=[financial_companion.models.accounts_model.only_int, django.core.validators.MinLengthValidator(6, 'Sort code must be 6 digits long')])),
                ('iban', encrypted_fields.fields.EncryptedCharField(blank=True, max_length=33, null=True, validators=[django.core.validators.MinLengthValidator(15, 'Iban must be a minimum of 15 characters long')])),
                ('interest_rate', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
            ],
            bases=('financial_companion.potaccount',),
        ),
    ]
