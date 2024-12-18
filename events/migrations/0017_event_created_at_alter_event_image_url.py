# Generated by Django 5.1 on 2024-12-02 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0016_rename_image_event_image_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='created_at',
            field=models.DateField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='image_url',
            field=models.ImageField(upload_to='event_images/', verbose_name='Event Image'),
        ),
    ]
