# Generated by Django 5.0.1 on 2024-03-22 16:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("firstapp", "0009_users_nickname"),
    ]

    operations = [
        migrations.AlterField(
            model_name="users",
            name="nickname",
            field=models.CharField(max_length=255),
        ),
    ]
