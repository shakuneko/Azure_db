# Generated by Django 5.0.1 on 2024-03-17 13:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("firstapp", "0003_alter_task_date_alter_task_time"),
    ]

    operations = [
        migrations.CreateModel(
            name="Gift",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("giftname", models.CharField(max_length=100)),
                ("image_url", models.URLField()),
            ],
        ),
    ]
