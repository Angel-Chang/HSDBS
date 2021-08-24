# Generated by Django 3.0 on 2021-03-04 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamecore', '0044_player_bind_player'),
    ]

    operations = [
        migrations.AddField(
            model_name='transfergold',
            name='jewel_type',
            field=models.PositiveIntegerField(choices=[(1, '金幣'), (2, '鑽石')], default=1, verbose_name='贈送貨幣種類'),
        ),
        migrations.AlterField(
            model_name='playergold',
            name='type',
            field=models.CharField(choices=[('11', '遊戲儲值'), ('12', '贈禮'), ('13', '收禮'), ('14', '抽水錢包提領'), ('15', '遊戲輸贏'), ('16', '官方補幣'), ('17', '購買配套')], default='11', max_length=2, verbose_name='類別'),
        ),
        migrations.AlterField(
            model_name='playerstar',
            name='star_type',
            field=models.CharField(choices=[('2', '見點獎金'), ('3', '匹配獎金'), ('4', '入金'), ('5', '出金'), ('6', '官方補幣'), ('7', '贈禮'), ('8', '收禮')], default='2', max_length=1, verbose_name='類別'),
        ),
        migrations.AlterField(
            model_name='starflow',
            name='starflow_type',
            field=models.CharField(choices=[('1', '玩家購買配套'), ('2', '見點獎金'), ('3', '匹配獎金'), ('4', '入金'), ('5', '出金'), ('6', '補幣')], default='1', max_length=1, verbose_name='類別'),
        ),
    ]