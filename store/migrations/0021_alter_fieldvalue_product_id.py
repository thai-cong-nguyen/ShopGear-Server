# Generated by Django 5.0 on 2024-01-01 13:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0020_field_field_type_fieldoption_value_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fieldvalue',
            name='product_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='field_values', to='store.product'),
        ),
    ]