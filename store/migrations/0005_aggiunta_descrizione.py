# Generated by Django 3.0.7 on 2020-06-17 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_aggiunta_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='description',
            field=models.TextField(null=True),
        ),
    ]
