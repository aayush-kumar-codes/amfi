# Generated by Django 2.2.2 on 2019-06-27 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0011_amc_next_amc_no'),
    ]

    operations = [
        migrations.AlterField(
            model_name='amc',
            name='next_amc_no',
            field=models.IntegerField(default=0),
        ),
    ]
