# Generated by Django 5.0.1 on 2024-03-27 15:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("firstapp", "0014_task_completed"),
    ]

    operations = [
        migrations.AddField(
            model_name="gift",
            name="description",
            field=models.CharField(default="", max_length=100),
        ),
        migrations.AddField(
            model_name="usergift",
            name="description",
            field=models.CharField(default="", max_length=100),
        ),
    ]
