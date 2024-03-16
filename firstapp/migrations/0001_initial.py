# Generated by Django 5.0.1 on 2024-03-16 03:02

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="booking",
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
                ("bid", models.CharField(default="0", max_length=50)),
                ("datatest", models.CharField(default="0", max_length=50)),
                ("exhibittype", models.CharField(max_length=20)),
                ("exhibitamount", models.CharField(max_length=5)),
                ("money", models.CharField(default="0", max_length=50)),
                ("which_date", models.DateField(auto_now=True)),
                ("which_time", models.TimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Task",
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
                ("task_name", models.CharField(max_length=255)),
                ("time", models.TimeField(blank=True, null=True)),
                ("date", models.DateField(blank=True, null=True)),
                ("category", models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="users",
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
                ("uid", models.CharField(max_length=50)),
                ("datatest", models.CharField(default="0", max_length=50)),
                ("created_time", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
