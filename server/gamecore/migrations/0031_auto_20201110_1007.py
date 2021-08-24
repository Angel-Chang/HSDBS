# Generated by Django 3.0 on 2020-11-10 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamecore', '0030_auto_20201109_2113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='bindcode',
            field=models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='綁定邀請碼'),
        ),
        migrations.AlterField(
            model_name='player',
            name='linkcode',
            field=models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='玩家邀請碼'),
        ),
    ]