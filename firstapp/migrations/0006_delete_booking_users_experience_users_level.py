# Generated by Django 5.0.1 on 2024-03-21 16:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("firstapp", "0005_usergift"),
    ]

    operations = [
        migrations.DeleteModel(
            name="booking",
        ),
        migrations.AddField(
            model_name="users",
            name="experience",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="users",
            name="level",
            field=models.IntegerField(default=1),
        ),
    ]
