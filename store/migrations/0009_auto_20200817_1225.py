# Generated by Django 3.1 on 2020-08-17 10:25

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_auto_20200817_1033'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='available_size',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('35', '35'), ('36', '36'), ('37', '37'), ('38', '38'), ('39', '39'), ('40', '40'), ('41', '41'), ('42', '42'), ('43', '43'), ('44', '44'), ('45', '45'), ('46', '46'), ('47', '47'), ('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL')], max_length=50, null=True),
        ),
    ]
