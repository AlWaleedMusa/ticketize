# Generated by Django 5.1 on 2024-12-03 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0021_alter_confirmationtoken_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='confirmationtoken',
            name='token',
            field=models.UUIDField(),
        ),
    ]
