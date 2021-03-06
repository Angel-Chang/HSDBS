# Generated by Django 3.0 on 2021-03-08 03:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamecore', '0047_auto_20210305_1019'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='introductiongold',
            name='player',
        ),
        migrations.RemoveField(
            model_name='playerwallet',
            name='player',
        ),
        migrations.RemoveField(
            model_name='gamerun',
            name='player1_agent_bonus',
        ),
        migrations.RemoveField(
            model_name='gamerun',
            name='player2_agent_bonus',
        ),
        migrations.RemoveField(
            model_name='gamerun',
            name='player3_agent_bonus',
        ),
        migrations.RemoveField(
            model_name='gamerun',
            name='player4_agent_bonus',
        ),
        migrations.RemoveField(
            model_name='gamerun',
            name='total_agent_bonus',
        ),
        migrations.RemoveField(
            model_name='player',
            name='agent_playerid',
        ),
        migrations.RemoveField(
            model_name='player',
            name='bonus_ratio',
        ),
        migrations.RemoveField(
            model_name='player',
            name='return_ratio',
        ),
        migrations.RemoveField(
            model_name='playergameroom',
            name='agent_commisson',
        ),
        migrations.RemoveField(
            model_name='playerroundresult',
            name='agent_bonus',
        ),
        migrations.AlterField(
            model_name='addvalue',
            name='type',
            field=models.CharField(choices=[('2', '補償'), ('8', '入金')], default='2', max_length=1, verbose_name='類型'),
        ),
        migrations.AlterField(
            model_name='goldflow',
            name='type',
            field=models.CharField(choices=[('1', '發行金幣'), ('2', '補幣'), ('6', '抽水')], default='2', max_length=1, verbose_name='類別'),
        ),
        migrations.AlterField(
            model_name='playergold',
            name='type',
            field=models.CharField(choices=[('1', '購買配套'), ('2', '官方補幣'), ('3', '贈禮'), ('4', '收禮'), ('5', '遊戲輸贏'), ('6', '抽水')], default='11', max_length=2, verbose_name='類別'),
        ),
        migrations.AlterField(
            model_name='playerstar',
            name='star_type',
            field=models.CharField(choices=[('1', '購買配套'), ('2', '官方補幣'), ('3', '贈禮'), ('4', '收禮'), ('5', '見點獎金'), ('6', '匹配獎金'), ('7', '出金'), ('8', '入金')], default='2', max_length=2, verbose_name='類別'),
        ),
        migrations.AlterField(
            model_name='starflow',
            name='starflow_type',
            field=models.CharField(choices=[('1', '玩家購買配套'), ('2', '補幣'), ('5', '見點獎金'), ('6', '匹配獎金'), ('7', '玩家出金'), ('8', '入金')], default='1', max_length=1, verbose_name='類別'),
        ),
        migrations.DeleteModel(
            name='GameResult',
        ),
        migrations.DeleteModel(
            name='IntroductionGold',
        ),
        migrations.DeleteModel(
            name='PlayerWallet',
        ),
    ]
