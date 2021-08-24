# Generated by Django 3.0 on 2021-04-07 23:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamecore', '0056_auto_20210328_1902'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='gold_total',
            field=models.FloatField(default=0, verbose_name='金幣'),
        ),
        migrations.AlterField(
            model_name='player',
            name='star',
            field=models.FloatField(default=0, verbose_name='鑽石'),
        ),
    ]
