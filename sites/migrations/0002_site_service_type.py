# Generated by Django 3.1.3 on 2021-06-02 23:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='service_type',
            field=models.CharField(blank=True, choices=[('nutanix', 'NUTANIX'), ('vmware', 'VMWARE')], max_length=64, null=True),
        ),
    ]