# Generated by Django 2.2.2 on 2019-09-18 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('amc', '0010_auto_20190918_1418'),
    ]

    operations = [
        migrations.CreateModel(
            name='Scheme_Name_Mismatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amc', models.TextField()),
                ('category', models.TextField()),
                ('subcategory', models.TextField()),
                ('name', models.TextField()),
            ],
        ),
    ]
