# Generated by Django 5.0.1 on 2024-01-06 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_alter_orderitem_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='status',
            field=models.IntegerField(choices=[(0, 'Đã qua sử dụng'), (1, ' Mới')], default=0),
        ),
    ]
