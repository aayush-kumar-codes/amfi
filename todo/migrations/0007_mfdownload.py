# Generated by Django 2.2.2 on 2019-06-24 05:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0006_auto_20190624_0420'),
    ]

    operations = [
        migrations.CreateModel(
            name='MFDownload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amc_id', models.IntegerField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField(null=True)),
            ],
        ),
    ]
