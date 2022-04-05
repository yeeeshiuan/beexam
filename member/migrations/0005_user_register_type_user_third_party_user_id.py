# Generated by Django 4.0.3 on 2022-04-05 06:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0004_user_is_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='register_type',
            field=models.CharField(choices=[('email', 'Email'), ('fb', 'Facebook'), ('google', 'Google')], default='email', max_length=16),
        ),
        migrations.AddField(
            model_name='user',
            name='third_party_user_id',
            field=models.PositiveBigIntegerField(default=None, null=True, unique=True, verbose_name='third party user_id'),
        ),
    ]
