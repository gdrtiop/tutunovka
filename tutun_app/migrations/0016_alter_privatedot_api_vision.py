# Generated by Django 5.0.3 on 2024-04-27 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutun_app', '0015_alter_privateroute_length_alter_privateroute_month_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='privatedot',
            name='api_vision',
            field=models.JSONField(null=True),
        ),
    ]
