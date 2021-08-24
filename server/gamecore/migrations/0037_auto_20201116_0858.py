# Generated by Django 3.0 on 2020-11-16 08:58

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('gamecore', '0036_vipseat'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vip',
            name='last_modify_date',
        ),
        migrations.RemoveField(
            model_name='vip',
            name='layer',
        ),
        migrations.RemoveField(
            model_name='vip',
            name='lower1_player',
        ),
        migrations.RemoveField(
            model_name='vip',
            name='lower1_seat',
        ),
        migrations.RemoveField(
            model_name='vip',
            name='lower2_player',
        ),
        migrations.RemoveField(
            model_name='vip',
            name='lower2_seat',
        ),
        migrations.RemoveField(
            model_name='vip',
            name='lower3_player',
        ),
        migrations.RemoveField(
            model_name='vip',
            name='lower3_seat',
        ),
        migrations.RemoveField(
            model_name='vip',
            name='upper_player',
        ),
        migrations.RemoveField(
            model_name='vip',
            name='upper_seat',
        ),
        migrations.AddField(
            model_name='vip',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='player',
            name='vip1000_seat',
            field=models.IntegerField(default=-1, verbose_name='VIP1000目前位置'),
        ),
        migrations.AlterField(
            model_name='player',
            name='vip100_seat',
            field=models.IntegerField(default=-1, verbose_name='VIP100目前位置'),
        ),
        migrations.AlterField(
            model_name='player',
            name='vip10_seat',
            field=models.IntegerField(default=-1, verbose_name='VIP10目前位置'),
        ),
        migrations.AlterField(
            model_name='player',
            name='vip2000_seat',
            field=models.IntegerField(default=-1, verbose_name='VIP2000目前位置'),
        ),
        migrations.AlterField(
            model_name='player',
            name='vip500_seat',
            field=models.IntegerField(default=-1, verbose_name='VIP500目前位置'),
        ),
        migrations.AlterField(
            model_name='player',
            name='vip50_seat',
            field=models.IntegerField(default=-1, verbose_name='VIP50目前位置'),
        ),
    ]