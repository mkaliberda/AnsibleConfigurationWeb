# Generated by Django 3.1.3 on 2021-02-15 02:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('playbook_generator', '0006_staticvarsvalue'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staticvarsfile',
            name='config_yaml_file',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='staticvarsfile',
            name='tag',
            field=models.CharField(blank=True, choices=[('nutanix', 'NUTANIX'), ('vmware', 'VMWARE')], max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='staticvarsvalue',
            name='service_type',
            field=models.CharField(blank=True, choices=[('nutanix', 'NUTANIX'), ('vmware', 'VMWARE')], max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='staticvarsvalue',
            name='value',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]