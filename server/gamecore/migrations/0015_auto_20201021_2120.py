# Generated by Django 3.0 on 2020-10-21 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamecore', '0014_auto_20201020_1113'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='bindcode',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='綁定邀請碼'),
        ),
        migrations.AddField(
            model_name='player',
            name='bonus_ratio',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='抽水成數(%)'),
        ),
        migrations.AddField(
            model_name='player',
            name='linkcode',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='玩家邀請碼'),
        ),
        migrations.AddField(
            model_name='player',
            name='return_ratio',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='給上層代理的回饋成數(%)'),
        ),
        migrations.AddField(
            model_name='playerwallet',
            name='withdraw_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='領取時間'),
        ),
        migrations.AlterField(
            model_name='introductiongold',
            name='withdraw_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='領取時間'),
        ),
        migrations.AlterField(
            model_name='player',
            name='permission_type',
            field=models.CharField(choices=[('1', '一般會員'), ('2', '代理會員')], default='1', max_length=1, verbose_name='會員身份'),
        ),
    ]