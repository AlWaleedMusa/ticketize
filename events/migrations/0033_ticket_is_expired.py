# Generated by Django 5.1 on 2024-12-21 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0032_event_status_alter_event_date_alter_event_image_url_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='is_expired',
            field=models.BooleanField(default=False, verbose_name='Is Expired'),
        ),
    ]
