# Generated by Django 3.1 on 2020-11-19 20:24

from django.db import migrations, models
from reversion.models import Version
from django.contrib.admin.models import LogEntry
import django.db.models.deletion
import json
import uuid
from ..containers import (
    SAMPLE_CONTAINER_KINDS,
    PARENT_CONTAINER_KINDS,
)


def remove_deleted_containers_versions(apps, schema_editor):
    # We restore deleted containers to ensure they are in the table so they receive a auto increment id
    container_model = apps.get_model("fms_core", "container")
    version_model = apps.get_model("reversion", "Version")
    deleted_containers = Version.objects.get_deleted(container_model)
    deleted_containers_ids = set(deleted_containers.values_list("object_id", flat=True))

    for version in version_model.objects.filter(content_type__model="container", object_id__in=deleted_containers_ids):
        # remove all revisions of the already deleted containers
        version.revision.delete()

        # update the django admin log entries for individuals
        for log in LogEntry.objects.filter(content_type__model="container", object_id=version.object_id):
            # Delete log entries
            log.delete()


def populate_foreign_keys(apps, schema_editor):
    container_model = apps.get_model("fms_core", "container")
    sample_model = apps.get_model("fms_core", "sample")
    version_model = apps.get_model("reversion", "Version")
    all_container_uuids = set(container_model.objects.all().values_list("id_old", flat=True))
    old_to_new_id_map = dict(container_model.objects.all().values_list("id_old", "id"))

    # update the sample and container FKs
    for sample in sample_model.objects.all():
        sample.container_new = old_to_new_id_map.get(sample.container)
        sample.save()
    for container in container_model.objects.all():
        if container.location:
            container.location_new = old_to_new_id_map.get(container.location)
        container.save()

    # update the version id to maintain old data with new structure
    for version in version_model.objects.filter(content_type__model="container", object_id__in=all_container_uuids):
        old_id = version.object_id
        # Convert old to new id
        version.object_id = old_to_new_id_map.get(uuid.UUID(hex=old_id))
        # Re-serialize data to fit new model
        data = json.loads(version.serialized_data)
        data[0]["pk"] = version.object_id
        if data[0]["fields"]["location"]:
            data[0]["fields"]["location"] = old_to_new_id_map.get(uuid.UUID(hex=data[0]["fields"]["location"]))
        version.serialized_data = json.dumps(data)
        # Save to database
        version.save()

    for version in version_model.objects.filter(content_type__model="sample"):
        # Fix old references to containers from samples
        data = json.loads(version.serialized_data)
        data[0]["fields"]["container"] = old_to_new_id_map.get(uuid.UUID(hex=data[0]["fields"]["container"]))
        version.serialized_data = json.dumps(data)
        # Save to database
        version.save()

    # update the django admin log entries for individuals
    for log in LogEntry.objects.filter(content_type__model="container", object_id__in=all_container_uuids):
        log.object_id = old_to_new_id_map.get(uuid.UUID(hex=log.object_id))
        # Save to database
        log.save()


class Migration(migrations.Migration):

    dependencies = [
        ('fms_core', '0008_v2_5_0'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='sample',
            unique_together={},
        ),
        migrations.RunPython(
            remove_deleted_containers_versions,
            migrations.RunPython.noop
        ),
        migrations.RenameField(
            model_name='container',
            old_name='id',
            new_name='id_old',
        ),
        migrations.AlterField(
            model_name='container',
            name='location',
            field=models.UUIDField(blank=True, null=True,
                                   help_text="An existing (parent) container this container is located inside of."),
        ),
        migrations.AlterField(
            model_name='sample',
            name='container',
            field=models.UUIDField(help_text="Designated location of the sample."),
        ),
        migrations.AlterField(
            model_name='container',
            name='id_old',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.RunSQL(
            "CREATE TABLE fms_core_container_temp AS TABLE fms_core_container",
            "DROP TABLE fms_core_container_temp"
        ),
        migrations.RunSQL(
            "DROP TABLE fms_core_container",
            migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            "CREATE TABLE fms_core_container AS TABLE fms_core_container_temp WITH NO DATA",
            migrations.RunSQL.noop
        ),
        migrations.AddField(
            model_name='container',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.RunSQL(
            "INSERT INTO fms_core_container SELECT * FROM fms_core_container_temp",
            migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            "DROP TABLE fms_core_container_temp",
            migrations.RunSQL.noop
        ),
        migrations.AddField(
            model_name='container',
            name='location_new',
            field=models.IntegerField(blank=True, null=True,
                                      help_text="An existing (parent) container this container is located inside of."),
        ),
        migrations.AddField(
            model_name='sample',
            name='container_new',
            field=models.IntegerField(blank=True, null=True, help_text="Designated location of the sample."),
        ),
        migrations.RunPython(
            populate_foreign_keys,
            migrations.RunPython.noop
        ),
        migrations.AlterField(
            model_name='sample',
            name='container_new',
            field=models.IntegerField(help_text="Designated location of the sample."),
        ),
        migrations.RenameField(
            model_name='sample',
            old_name='container',
            new_name='container_old',
        ),
        migrations.RenameField(
            model_name='sample',
            old_name='container_new',
            new_name='container_id',
        ),
        migrations.RenameField(
            model_name='container',
            old_name='location',
            new_name='location_old',
        ),
        migrations.RenameField(
            model_name='container',
            old_name='location_new',
            new_name='location_id',
        ),
        migrations.RunSQL(
            "ALTER TABLE fms_core_sample ADD CONSTRAINT fk_container FOREIGN KEY (container_id) REFERENCES fms_core_container(id)",
            "ALTER TABLE fms_core_sample DROP CONSTRAINT fk_container;"
        ),
        migrations.RunSQL(
            "ALTER TABLE fms_core_container ADD CONSTRAINT fk_location FOREIGN KEY (location_id) REFERENCES fms_core_container(id)",
            "ALTER TABLE fms_core_container DROP CONSTRAINT fk_location;"
        ),
        migrations.RenameField(
            model_name='sample',
            old_name='container_id',
            new_name='container',
        ),
        migrations.RenameField(
            model_name='container',
            old_name='location_id',
            new_name='location',
        ),
        migrations.RemoveField(
            model_name='container',
            name='id_old',
        ),
        migrations.RemoveField(
            model_name='container',
            name='location_old',
        ),
        migrations.RemoveField(
            model_name='sample',
            name='container_old',
        ),
        migrations.AlterField(
            model_name='container',
            name='location',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.PROTECT,
                                    related_name="children",
                                    limit_choices_to={"kind__in": PARENT_CONTAINER_KINDS},
                                    help_text="An existing (parent) container this container is located inside of.",
                                    to='fms_core.container'),
        ),
        migrations.AlterField(
            model_name='sample',
            name='container',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                    related_name="samples",
                                    limit_choices_to={"kind__in": SAMPLE_CONTAINER_KINDS},
                                    help_text="Designated location of the sample.",
                                    to='fms_core.container'),
        ),
        migrations.AlterUniqueTogether(
            name='sample',
            unique_together={('container', 'coordinates')},
        ),
    ]
