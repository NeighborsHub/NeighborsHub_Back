# Generated by Django 4.2.7 on 2024-01-04 09:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
        ('albums', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='useravatar',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='%(class)ss_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='useravatar',
            name='hashtags',
            field=models.ManyToManyField(blank=True, to='core.hashtag'),
        ),
        migrations.AddField(
            model_name='useravatar',
            name='state',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.states'),
        ),
        migrations.AddField(
            model_name='useravatar',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='%(class)ss_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='useravatar',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='media',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='%(class)ss_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='media',
            name='hashtags',
            field=models.ManyToManyField(blank=True, to='core.hashtag'),
        ),
        migrations.AddField(
            model_name='media',
            name='state',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.states'),
        ),
        migrations.AddField(
            model_name='media',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='%(class)ss_updated_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
