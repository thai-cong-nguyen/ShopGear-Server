# Generated by Django 5.0.1 on 2024-01-11 03:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_alter_order_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='review',
            field=models.IntegerField(choices=[(0, 'Đang chờ duyệt'), (1, 'Đã duyệt'), (2, 'Đã từ chối')], default=0),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.IntegerField(choices=[(1, 'Đang chờ xác nhận'), (2, 'Đang chờ thanh toán'), (3, 'Đang vận chuyển'), (4, 'Đã giao hàng'), (5, 'Đã huỷ')], default=1),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='confirmation_status',
            field=models.IntegerField(choices=[(1, 'Đang chờ xác nhận'), (2, 'Đang chờ thanh toán'), (3, 'Đang vận chuyển'), (4, 'Đã giao hàng'), (5, 'Đã huỷ')], default=1),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='status',
            field=models.IntegerField(choices=[(1, 'Đang chờ xác nhận'), (2, 'Đang chờ thanh toán'), (3, 'Đang vận chuyển'), (4, 'Đã giao hàng'), (5, 'Đã huỷ')], default=1),
        ),
    ]
