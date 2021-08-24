# Generated by Django 3.0 on 2020-08-31 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamecore', '0008_auto_20200614_2337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='gold_total',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=20, verbose_name='金幣'),
        ),
    ]