# Generated by Django 4.2.7 on 2024-04-18 14:21

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_chatmessage_deleted_by_chatroom_admin_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessage',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='chatroom',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='chatroom',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]