# Generated by Django 4.2.7 on 2024-01-04 09:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('post', '0006_comment_hashtags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='likecomment',
            name='like_ptr',
        ),
        migrations.RemoveField(
            model_name='likepost',
            name='like_ptr',
        ),
        migrations.AddField(
            model_name='likecomment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='likecomment',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='%(class)ss_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='likecomment',
            name='hashtags',
            field=models.ManyToManyField(blank=True, to='core.hashtag'),
        ),
        migrations.AddField(
            model_name='likecomment',
            name='id',
            field=models.BigAutoField(auto_created=True, default=1, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='likecomment',
            name='state',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.states'),
        ),
        migrations.AddField(
            model_name='likecomment',
            name='type',
            field=models.CharField(choices=[('support', 'Support'), ('like', 'Like'), ('dislike', 'Dislike')], default=django.utils.timezone.now, max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='likecomment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='likecomment',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='%(class)ss_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='likepost',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='likepost',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='%(class)ss_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='likepost',
            name='hashtags',
            field=models.ManyToManyField(blank=True, to='core.hashtag'),
        ),
        migrations.AddField(
            model_name='likepost',
            name='id',
            field=models.BigAutoField(auto_created=True, default=django.utils.timezone.now, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='likepost',
            name='state',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.states'),
        ),
        migrations.AddField(
            model_name='likepost',
            name='type',
            field=models.CharField(choices=[('support', 'Support'), ('like', 'Like'), ('dislike', 'Dislike')], default=django.utils.timezone.now, max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='likepost',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='likepost',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='%(class)ss_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='Like',
        ),
    ]
