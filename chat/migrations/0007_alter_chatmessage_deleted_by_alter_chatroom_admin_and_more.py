# Generated by Django 4.2.7 on 2024-04-25 14:35

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat', '0006_chatmessage_post_chatmessage_reply_to_chatroom_post'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatmessage',
            name='deleted_by',
            field=models.ManyToManyField(blank=True, related_name='deleted_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='chatroom',
            name='admin',
            field=models.ManyToManyField(blank=True, related_name='admin', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='chatroom',
            name='member',
            field=models.ManyToManyField(blank=True, related_name='member', to=settings.AUTH_USER_MODEL),
        ),
    ]