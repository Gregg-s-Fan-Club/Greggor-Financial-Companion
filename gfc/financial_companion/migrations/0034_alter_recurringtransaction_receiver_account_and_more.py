# Generated by Django 4.1.3 on 2023-03-18 11:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('financial_companion', '0033_merge_20230311_1426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recurringtransaction',
            name='receiver_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver%(app_label)s_%(class)s_related', to='financial_companion.account'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='receiver_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver%(app_label)s_%(class)s_related', to='financial_companion.account'),
        ),
    ]
