# Generated by Django 4.2.7 on 2023-11-20 04:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_alter_post_zone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='zone',
            field=models.CharField(choices=[('HCM', 'Hồ Chí Minh'), ('DN', 'Đà Nẵng'), ('HN', 'Hà Nội')], default='HCM', max_length=4),
        ),
    ]
