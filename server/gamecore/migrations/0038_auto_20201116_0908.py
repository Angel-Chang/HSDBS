# Generated by Django 3.0 on 2020-11-16 09:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gamecore', '0037_auto_20201116_0858'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vip',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamecore.Player', verbose_name='玩家ID'),
        ),
    ]
