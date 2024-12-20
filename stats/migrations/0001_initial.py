# Generated by Django 2.2.2 on 2019-07-14 05:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('todo', '0017_auto_20190711_0912'),
    ]

    operations = [
        migrations.CreateModel(
            name='SchemeStats',
            fields=[
                ('scheme', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='todo.Scheme')),
                ('dump', models.TextField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('calc_date', models.DateField()),
                ('one_year_abs_ret', models.FloatField()),
                ('three_year_abs_ret', models.FloatField()),
                ('three_year_cagr_ret', models.FloatField()),
                ('five_year_abs_ret', models.FloatField()),
                ('five_year_cagr_ret', models.FloatField()),
                ('ten_year_abs_ret', models.FloatField()),
                ('ten_year_cagr_ret', models.FloatField()),
                ('since_begin_abs_ret', models.FloatField()),
                ('since_begin_cagr_ret', models.FloatField()),
            ],
        ),
    ]
