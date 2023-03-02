# Generated by Django 4.1 on 2023-03-01 21:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tapio", "0005_modifiedsource_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="report",
            name="sources",
        ),
        migrations.AddField(
            model_name="report",
            name="sources",
            field=models.ManyToManyField(
                blank=True, null=True, related_name="reports", to="tapio.source"
            ),
        ),
    ]
