# Generated by Django 4.1 on 2023-03-03 05:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tapio", "0008_report_scenarios"),
    ]

    operations = [
        migrations.AlterField(
            model_name="report",
            name="scenarios",
            field=models.JSONField(
                default=dict,
                help_text="list of modified sources per scenario {scenario_1 : [{'s_id1' : 'ms_id1'}, ..], scenario_2 : [{'s_id1' : 'ms_id2'}, ..]}",
            ),
        ),
    ]
