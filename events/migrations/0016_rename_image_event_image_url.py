# Generated by Django 5.1 on 2024-12-02 11:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0015_event_image'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='image',
            new_name='image_url',
        ),
    ]
