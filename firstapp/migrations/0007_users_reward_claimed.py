# Generated by Django 5.0.1 on 2024-03-21 17:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("firstapp", "0006_delete_booking_users_experience_users_level"),
    ]

    operations = [
        migrations.AddField(
            model_name="users",
            name="reward_claimed",
            field=models.BooleanField(default=False),
        ),
    ]
