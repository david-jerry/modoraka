# Generated by Django 4.2.8 on 2024-01-23 14:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("subscription", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="feature",
            name="no_of_groups",
            field=models.IntegerField(default=1),
        ),
    ]
