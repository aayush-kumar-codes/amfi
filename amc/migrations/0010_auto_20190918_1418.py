# Generated by Django 2.2.2 on 2019-09-18 14:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('amc', '0009_auto_20190918_1415'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scheme_ter_process_log',
            name='process',
        ),
        migrations.DeleteModel(
            name='Scheme_TER_Process',
        ),
        migrations.DeleteModel(
            name='Scheme_TER_Process_Log',
        ),
    ]
