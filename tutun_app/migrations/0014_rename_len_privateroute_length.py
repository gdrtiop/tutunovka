# Generated by Django 5.0.3 on 2024-04-27 16:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutun_app', '0013_privateroute_len_privateroute_month_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='privateroute',
            old_name='len',
            new_name='length',
        ),
    ]
