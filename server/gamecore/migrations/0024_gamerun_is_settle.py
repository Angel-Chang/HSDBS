# Generated by Django 3.0 on 2020-11-04 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamecore', '0023_auto_20201030_2313'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamerun',
            name='is_settle',
            field=models.BooleanField(default=False, verbose_name='是否已結算過'),
        ),
    ]
