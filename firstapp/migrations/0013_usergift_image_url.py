# Generated by Django 5.0.1 on 2024-03-24 07:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("firstapp", "0012_users_image_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="usergift",
            name="image_url",
            field=models.URLField(default=""),
            preserve_default=False,
        ),
    ]
