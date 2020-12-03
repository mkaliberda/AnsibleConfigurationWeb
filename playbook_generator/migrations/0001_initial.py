# Generated by Django 3.1.3 on 2020-11-30 19:37

from django.db import migrations, models
import jsonfield.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ConfigUpload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_delete', models.BooleanField(default=False)),
                ('parsed_data', jsonfield.fields.JSONField()),
                ('config_yml_file', models.FileField(upload_to='')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
