# Generated by Django 5.2 on 2025-05-11 19:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0009_rename_order_chapter_number_chapter_adventure_hook_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='campaign',
            old_name='user_description',
            new_name='description',
        ),
    ]
