# Generated by Django 4.2.7 on 2023-11-25 08:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_rename_user_product_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='user_id',
            field=models.ForeignKey(db_column='user_id', default=None, on_delete=django.db.models.deletion.CASCADE, to='store.user'),
        ),
    ]
