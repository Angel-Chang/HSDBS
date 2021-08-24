# Generated by Django 3.0 on 2020-11-04 15:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gamecore', '0024_gamerun_is_settle'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlayerRoundResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('base', models.PositiveIntegerField(verbose_name='底數')),
                ('win', models.PositiveIntegerField(default=0, verbose_name='胡牌')),
                ('lost_won', models.PositiveIntegerField(default=0, verbose_name='放槍')),
                ('win_self_hand', models.PositiveIntegerField(default=0, verbose_name='自摸')),
                ('banker', models.PositiveIntegerField(default=0, verbose_name='莊家')),
                ('score', models.IntegerField(default=0, verbose_name='成績')),
                ('start_gold', models.DecimalField(decimal_places=4, default=0, max_digits=20, verbose_name='起始金額')),
                ('settle_gold', models.DecimalField(decimal_places=4, default=0, max_digits=20, verbose_name='結算金額')),
                ('commission', models.DecimalField(decimal_places=7, default=0, max_digits=20, verbose_name='官方抽水金額')),
                ('agent_commisson', models.DecimalField(decimal_places=7, default=0, max_digits=20, verbose_name='代理抽水金額')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('game_run', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamecore.GameRun', verbose_name='遊戲局號(回播碼)')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamecore.Player', verbose_name='玩家ID')),
            ],
        ),
    ]
