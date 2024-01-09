# Generated by Django 5.0.1 on 2024-01-08 17:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='confirmation_status',
            field=models.IntegerField(choices=[(1, 'Đang chờ xác nhận'), (2, ' Chưa thanh toán'), (3, 'Đã thanh toán'), (4, 'Đang vận chuyển'), (5, 'Đã giao hàng'), (6, 'Chờ huỷ'), (0, 'Đã huỷ')], default=1),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='seller',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='seller', to='store.user'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.IntegerField(choices=[(1, 'Đang chờ xác nhận'), (2, ' Chưa thanh toán'), (3, 'Đã thanh toán'), (4, 'Đang vận chuyển'), (5, 'Đã giao hàng'), (6, 'Chờ huỷ'), (0, 'Đã huỷ')], default=1),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='status',
            field=models.IntegerField(choices=[(1, 'Đang chờ xác nhận'), (2, ' Chưa thanh toán'), (3, 'Đã thanh toán'), (4, 'Đang vận chuyển'), (5, 'Đã giao hàng'), (6, 'Chờ huỷ'), (0, 'Đã huỷ')], default=1),
        ),
        migrations.DeleteModel(
            name='SellOrder',
        ),
    ]