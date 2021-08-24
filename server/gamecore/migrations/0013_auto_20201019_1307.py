# Generated by Django 3.0 on 2020-10-19 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamecore', '0012_gameresult_base'),
    ]

    operations = [
        migrations.AddField(
            model_name='goldflow',
            name='admin_account',
            field=models.CharField(default='', max_length=150, verbose_name='管理者帳號'),
        ),
        migrations.AddField(
            model_name='transfergold',
            name='receiver_gold',
            field=models.PositiveIntegerField(default=0, verbose_name='接收人轉幣前金額'),
        ),
        migrations.AddField(
            model_name='transfergold',
            name='sender_gold',
            field=models.PositiveIntegerField(default=0, verbose_name='贈送人轉幣前金額'),
        ),
        migrations.AlterField(
            model_name='gameroom',
            name='state',
            field=models.CharField(choices=[('1', '等待中'), ('2', '進行中'), ('3', '結束')], default='1', max_length=1, verbose_name='遊戲狀態'),
        ),
    ]