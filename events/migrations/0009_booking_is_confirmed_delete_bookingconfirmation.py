# Generated by Django 5.1 on 2024-11-30 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_bookingconfirmation'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='is_confirmed',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='BookingConfirmation',
        ),
    ]
