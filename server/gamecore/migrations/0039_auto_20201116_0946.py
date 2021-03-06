# Generated by Django 3.0 on 2020-11-16 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamecore', '0038_auto_20201116_0908'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='vip1000_seat',
            field=models.IntegerField(default=0, verbose_name='VIP1000目前位置'),
        ),
        migrations.AlterField(
            model_name='player',
            name='vip100_seat',
            field=models.IntegerField(default=0, verbose_name='VIP100目前位置'),
        ),
        migrations.AlterField(
            model_name='player',
            name='vip10_seat',
            field=models.IntegerField(default=0, verbose_name='VIP10目前位置'),
        ),
        migrations.AlterField(
            model_name='player',
            name='vip2000_seat',
            field=models.IntegerField(default=0, verbose_name='VIP2000目前位置'),
        ),
        migrations.AlterField(
            model_name='player',
            name='vip500_seat',
            field=models.IntegerField(default=0, verbose_name='VIP500目前位置'),
        ),
        migrations.AlterField(
            model_name='player',
            name='vip50_seat',
            field=models.IntegerField(default=0, verbose_name='VIP50目前位置'),
        ),
    ]
