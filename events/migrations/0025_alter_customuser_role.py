# Generated by Django 5.1 on 2024-12-08 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0024_event_staff'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('organizer', 'Organizer'), ('checkin-staff', 'Check-in Staff')], default='organizer', max_length=20),
        ),
    ]
