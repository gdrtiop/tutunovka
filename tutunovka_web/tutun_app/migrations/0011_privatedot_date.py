# Generated by Django 5.0.3 on 2024-04-03 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutun_app', '0010_note_remove_privateroute_note_privateroute_note'),
    ]

    operations = [
        migrations.AddField(
            model_name='privatedot',
            name='date',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]
