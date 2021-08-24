# Generated by Django 3.0 on 2020-11-12 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamecore', '0033_auto_20201112_1023'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamerun',
            name='banker_player',
            field=models.PositiveIntegerField(default=0, verbose_name='莊家'),
        ),
        migrations.AlterField(
            model_name='gamerun',
            name='lost_won_player',
            field=models.PositiveIntegerField(default=0, verbose_name='放槍'),
        ),
        migrations.AlterField(
            model_name='gamerun',
            name='win_player',
            field=models.PositiveIntegerField(default=0, verbose_name='胡牌'),
        ),
        migrations.AlterField(
            model_name='gamerun',
            name='win_self_hand_player',
            field=models.PositiveIntegerField(default=0, verbose_name='自摸'),
        ),
    ]
