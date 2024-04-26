# Generated by Django 4.2.7 on 2024-04-18 14:19

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat', '0003_rename_roomid_chatroom_room_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessage',
            name='deleted_by',
            field=models.ManyToManyField(related_name='deleted_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='chatroom',
            name='admin',
            field=models.ManyToManyField(related_name='admin', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='chatroom',
            name='member',
            field=models.ManyToManyField(related_name='member', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='chatroom',
            name='type',
            field=models.CharField(choices=[('direct', 'Direct Chat'), ('group', 'Group')], default='direct', max_length=10),
        ),
    ]