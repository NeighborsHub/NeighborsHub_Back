# Generated by Django 4.2.7 on 2023-12-29 18:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('post', '0003_remove_post_hashtags_posthashtag'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='hashtags',
            field=models.ManyToManyField(blank=True, through='post.PostHashtag', to='core.hashtag'),
        ),
    ]