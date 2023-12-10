# Generated by Django 4.2.7 on 2023-12-10 09:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customeruser',
            name='city',
        ),
        migrations.RemoveField(
            model_name='customeruser',
            name='street',
        ),
        migrations.RemoveField(
            model_name='customeruser',
            name='zip_code',
        ),
        migrations.AddField(
            model_name='customeruser',
            name='birth_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('basemodel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.basemodel')),
                ('follower', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='follower', to='users.customeruser')),
                ('following', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='following', to='users.customeruser')),
            ],
            bases=('core.basemodel',),
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('basemodel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.basemodel')),
                ('street', models.CharField(blank=True, max_length=255, null=True)),
                ('zip_code', models.CharField(blank=True, max_length=10, null=True)),
                ('is_main_address', models.BooleanField(default=False)),
                ('city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.city')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.customeruser')),
            ],
            bases=('core.basemodel',),
        ),
    ]
