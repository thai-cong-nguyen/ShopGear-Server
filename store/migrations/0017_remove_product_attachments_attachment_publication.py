# Generated by Django 5.0 on 2024-01-01 05:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0016_attachment_product_attachments'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='attachments',
        ),
        migrations.AddField(
            model_name='attachment',
            name='publication',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='store.product', verbose_name='Model that uses the image field'),
        ),
    ]