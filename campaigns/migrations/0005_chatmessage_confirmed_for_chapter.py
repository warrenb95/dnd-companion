# Generated by Django 5.2 on 2025-04-23 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("campaigns", "0004_alter_sessionnote_date_chatmessage"),
    ]

    operations = [
        migrations.AddField(
            model_name="chatmessage",
            name="confirmed_for_chapter",
            field=models.BooleanField(default=False),
        ),
    ]
