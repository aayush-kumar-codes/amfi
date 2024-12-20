# Generated by Django 2.2.2 on 2019-07-16 12:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0017_auto_20190711_0912'),
        ('amc', '0005_scheme_portfolio_data_scheme'),
    ]

    operations = [
        migrations.CreateModel(
            name='Scheme_TER_Process',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amc', models.TextField()),
                ('file_name', models.TextField()),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Scheme_TER_Process_Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log', models.TextField()),
                ('level', models.CharField(max_length=255)),
                ('process', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='amc.Scheme_TER_Process')),
            ],
        ),
        migrations.CreateModel(
            name='Scheme_TER',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('ter', models.FloatField()),
                ('scheme', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='todo.Scheme')),
            ],
        ),
    ]
