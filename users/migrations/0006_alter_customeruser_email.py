# Generated by Django 4.2.7 on 2023-12-16 02:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_customeruser_is_verified_email_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customeruser',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, unique=True),
        ),
    ]