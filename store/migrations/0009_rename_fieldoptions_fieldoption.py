# Generated by Django 5.0 on 2024-01-01 03:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_alter_product_user_id_field_fieldoptions'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='FieldOptions',
            new_name='FieldOption',
        ),
    ]