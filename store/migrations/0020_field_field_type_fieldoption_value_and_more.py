# Generated by Django 5.0 on 2024-01-01 08:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0019_post_created_at_post_updated_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='field',
            name='field_type',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fieldoption',
            name='value',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='field',
            name='category_id',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='store.category'),
        ),
        migrations.CreateModel(
            name='FieldValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=255)),
                ('field_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.field')),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product')),
            ],
        ),
    ]