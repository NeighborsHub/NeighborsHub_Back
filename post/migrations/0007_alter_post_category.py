# Generated by Django 4.2.7 on 2024-02-28 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0006_post_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='category',
            field=models.ManyToManyField(blank=True, to='post.category', verbose_name='category'),
        ),
    ]
