# Generated by Django 5.2 on 2025-05-15 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0010_rename_user_description_campaign_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='encounter',
            name='map_image',
            field=models.ImageField(blank=True, upload_to='images/'),
        ),
    ]
