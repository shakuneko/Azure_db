# Generated by Django 5.0.1 on 2024-03-16 17:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("firstapp", "0002_task_tid"),
    ]

    operations = [
        migrations.AlterField(
            model_name="task",
            name="date",
            field=models.DateField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="task",
            name="time",
            field=models.TimeField(blank=True, max_length=50, null=True),
        ),
    ]
