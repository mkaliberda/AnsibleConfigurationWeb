# Generated by Django 3.1.3 on 2021-06-12 22:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('playbook_generator', '0011_configupload_service_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='staticvarsvalue',
            name='is_common_location',
            field=models.BooleanField(blank=True, default=False, help_text='makes effect on creatong default vars for location', null=True),
        ),
    ]