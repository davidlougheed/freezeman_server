# Generated by Django 3.1 on 2021-01-27 21:41

from django.db import migrations



class Migration(migrations.Migration):

    dependencies = [
        ('fms_core', '0011_v3_0_0'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sample',
            old_name='reception_date',
            new_name='creation_date',
        ),
    ]
