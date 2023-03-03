# Generated by Django 4.1 on 2023-03-03 10:54
from django.core.management import call_command
from django.db import migrations


def load_initial_data(apps, schema_editor):
    fixtures = [
        "companies.json",
        "units.json",
        "sources.json",
        "modifiedSources.json",
        "reports.json"
    ]
    for fixture in fixtures:
        call_command("loaddata", fixture)

class Migration(migrations.Migration):
    dependencies = [
        ("tapio", "0010_report_year"),
    ]

    operations = [
        migrations.RunPython(load_initial_data)
    ]
