# Generated by Django 3.0 on 2020-06-14 23:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamecore', '0007_auto_20200606_2022'),
    ]

    operations = [
        migrations.AlterField(
            model_name='addvalue',
            name='description',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='補幣事由'),
        ),
    ]
