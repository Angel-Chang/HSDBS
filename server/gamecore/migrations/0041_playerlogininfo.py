# Generated by Django 3.0 on 2020-11-20 10:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gamecore', '0040_auto_20201118_0934'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlayerLoginInfo',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('login_date', models.DateTimeField(auto_now=True, verbose_name='登入時間')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamecore.Player', verbose_name='登入帳號ID')),
            ],
        ),
    ]
