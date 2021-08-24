# Generated by Django 3.0 on 2021-05-16 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamecore', '0059_auto_20210516_1749'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='goldflow',
            index=models.Index(fields=['type', 'created_date'], name='gamecore_go_type_d99f04_idx'),
        ),
        migrations.AddIndex(
            model_name='playergold',
            index=models.Index(fields=['player', 'type', 'created_date'], name='gamecore_pl_player__c2d7fa_idx'),
        ),
        migrations.AddIndex(
            model_name='playerstar',
            index=models.Index(fields=['star_type', 'created_date'], name='gamecore_pl_star_ty_afe170_idx'),
        ),
        migrations.AddIndex(
            model_name='starflow',
            index=models.Index(fields=['starflow_type', 'created_date'], name='gamecore_st_starflo_f61f42_idx'),
        ),
        migrations.AddIndex(
            model_name='transfergold',
            index=models.Index(fields=['jewel_type', 'sender_id', 'created_date'], name='gamecore_tr_jewel_t_8042c7_idx'),
        ),
        migrations.AddIndex(
            model_name='transfergold',
            index=models.Index(fields=['jewel_type', 'receiver_id', 'created_date'], name='gamecore_tr_jewel_t_467e2b_idx'),
        ),
        migrations.AddIndex(
            model_name='vipbonus',
            index=models.Index(fields=['vip_type', 'seat', 'created_date'], name='gamecore_vi_vip_typ_9fd1c4_idx'),
        ),
        migrations.AddIndex(
            model_name='viptree',
            index=models.Index(fields=['vip_type', 'seat'], name='gamecore_vi_vip_typ_b5fbcd_idx'),
        ),
    ]
