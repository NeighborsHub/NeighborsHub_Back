# Generated by Django 4.2.7 on 2024-02-08 21:27

import albums.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('albums', '0005_alter_useravatar_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='file',
            field=models.FileField(upload_to=albums.models.UserFileSystemStorage.get_user_upload_path),
        ),
    ]
