# Generated by Django 5.1 on 2024-11-29 01:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='link',
            field=models.URLField(default='http://127.0.0.1:8000/event/571a284c-4dd6-4b35-954f-e94aaa749311/', max_length=500),
            preserve_default=False,
        ),
    ]
