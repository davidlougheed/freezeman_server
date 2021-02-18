# Generated by Django 3.1 on 2021-02-17 22:15

from django.db import migrations, models
import django.utils.timezone
import django.db.models.deletion
import json

SAMPLE_KINDS = ['DNA', 'RNA', 'BLOOD', 'CELLS', 'EXPECTORATION', 'GARGLE', 'PLASMA', 'SALIVA', 'SWAB']


def create_sample_kinds(apps, schema_editor):
    SampleKind = apps.get_model("fms_core", "SampleKind")
    for kind in SAMPLE_KINDS:
        SampleKind.objects.create(name=kind)


def copy_samples_kinds(apps, schema_editor):
    Sample = apps.get_model("fms_core", "Sample")
    SampleKind = apps.get_model("fms_core", "SampleKind")
    sample_kind_ids_by_name = {sample_kind.name: sample_kind.id for sample_kind in SampleKind.objects.all()}

    for sample in Sample.objects.all():
        name = sample.biospecimen_type
        sample.sample_kind_id = sample_kind_ids_by_name[name]
        sample.save()

    # Deals with versions
    Version = apps.get_model("reversion", "Version")
    SampleKind = apps.get_model("fms_core", "SampleKind")
    sample_kind_ids_by_name = {sample_kind.name: sample_kind.id for sample_kind in SampleKind.objects.all()}

    for version in Version.objects.filter(content_type__model="sample"):
        data = json.loads(version.serialized_data)
        if 'biospecimen_type' in data[0]["fields"]:
            biospecimen_type = data[0]["fields"]["biospecimen_type"]
            data[0]["fields"]["sample_kind"] = sample_kind_ids_by_name[biospecimen_type]
            data[0]["fields"].pop("biospecimen_type", None)
        version.serialized_data = json.dumps(data)
        version.save()


def create_lineage_from_extracted(apps, schema_editor):
    sample_model = apps.get_model("fms_core", "sample")
    version_model = apps.get_model("reversion", "Version")

    # Create parent lineage for each sample that had an extracted_from fk
    for sample in sample_model.objects.all():
        if sample.old_extracted_from:
            sample.add_parent_lineage(sample.old_extracted_from)

    for version in version_model.objects.filter(content_type__model="sample"):
        # Remove the extracted_from field from the serialized_data in version
        data = json.loads(version.serialized_data)
        data[0]["fields"].pop("extracted_from", None)
        version.serialized_data = json.dumps(data)
        # Save to database
        version.save()


class Migration(migrations.Migration):

    dependencies = [
        ('fms_core', '0013_v3_0_1'),
    ]

    operations = [
        # Migrations related to SampleKind replacing Sample.biospecimen_type
        migrations.CreateModel(
            name='SampleKind',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Biological material collected from study subject during the conduct of a genomic study project.', max_length=200)),
                ('molecule_ontology_curie', models.CharField(blank=True, help_text='SO ontology term to describe an molecule, such as ‘SO:0000991’ (‘genomic_DNA’)', max_length=20)),
            ],
        ),
        migrations.AddField(
            model_name='sample',
            name='sample_kind',
            field=models.ForeignKey(
                blank=True,
                null=True,
                help_text='Biological material collected from study subject during the conduct of a genomic study project.',
                on_delete=django.db.models.deletion.PROTECT,
                to='fms_core.samplekind'),
        ),
        migrations.RunPython(
            create_sample_kinds,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunPython(
            copy_samples_kinds,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RemoveField(
            model_name='sample',
            name='biospecimen_type',
        ),
        migrations.AlterField(
            model_name='sample',
            name='sample_kind',
            field=models.ForeignKey(
                help_text='Biological material collected from study subject during the conduct of a genomic study project.',
                on_delete=django.db.models.deletion.PROTECT, to='fms_core.samplekind'),
        ),
        migrations.AlterField(
            model_name='samplekind',
            name='name',
            field=models.CharField(
                help_text='Biological material collected from study subject during the conduct of a genomic study project.',
                max_length=200, unique=True),
        ),
        # Migrations related to Process, Protocol and ProcessBySample
        migrations.CreateModel(
            name='Process',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(blank=True, help_text='Relevant information about the process.')),
            ],
        ),
        migrations.CreateModel(
            name='Protocol',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Unique identifier for the protocol.', max_length=200, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProcessBySample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('execution_date', models.DateField(default=django.utils.timezone.now, help_text='Date of execution of the process.')),
                ('volume_used', models.DecimalField(blank=True, decimal_places=3, help_text='Volume of the sample used, in µL.', max_digits=20, null=True)),
                ('comment', models.TextField(blank=True, help_text='Other relevant information.')),
                ('process', models.ForeignKey(help_text='Process', on_delete=django.db.models.deletion.PROTECT, related_name='process_by_sample', to='fms_core.process')),
                ('sample', models.ForeignKey(help_text='Sample', on_delete=django.db.models.deletion.PROTECT, related_name='process_by_sample', to='fms_core.sample')),
            ],
        ),
        migrations.AddField(
            model_name='process',
            name='protocol',
            field=models.ForeignKey(help_text='Protocol', on_delete=django.db.models.deletion.PROTECT, related_name='processes', to='fms_core.protocol'),
        ),
        migrations.CreateModel(
            name='SampleLineage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('child', models.ForeignKey(help_text='Child sample', on_delete=django.db.models.deletion.CASCADE,
                                            related_name='child_sample', to='fms_core.sample')),
                ('parent', models.ForeignKey(help_text='Parent sample', on_delete=django.db.models.deletion.CASCADE,
                                             related_name='parent_sample', to='fms_core.sample')),
            ],
        ),
        migrations.RenameField(
            model_name='sample',
            old_name='extracted_from',
            new_name='old_extracted_from',
        ),
        migrations.AddField(
            model_name='sample',
            name='child_of',
            field=models.ManyToManyField(blank=True, related_name='parent_of', through='fms_core.SampleLineage',
                                         to='fms_core.Sample'),
        ),
        migrations.RunPython(
            create_lineage_from_extracted,
            migrations.RunPython.noop
        ),
        migrations.RemoveField(
            model_name='sample',
            name='old_extracted_from',
        ),
    ]
