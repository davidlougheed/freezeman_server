from decimal import Decimal


def create_container(barcode, location=None):
    return dict(
        kind='tube rack 8x12',
        name='TestRack001',
        barcode=barcode,
        coordinates='',
        location=location,
        comment=''
    )


def create_sample_container(kind, name, barcode, coordinates='', location=None):
    return dict(
        kind=kind,
        name=name,
        barcode=barcode,
        coordinates=coordinates,
        location=location,
        comment=''
    )


def create_sample(individual, container, coordinates='', **kwargs):
    return dict(
        biospecimen_type='BLOOD',
        name='test_sample_01',
        alias='53',
        individual=individual,
        volume_history=[
            {
                "date": "2020-04-15T03:50:45.127218Z",
                "update_type": "update",
                "volume_value": "5000"
            }
        ],
        # concentration=Decimal('0.02'),
        experimental_group=['EG01', 'EG02'],
        collection_site='Site1',
        container=container,
        coordinates=coordinates,
        **kwargs
    )


def create_extracted_sample(biospecimen_type, individual, container, extracted_from, volume_used, coordinates=''):
    return dict(
        biospecimen_type=biospecimen_type,
        name='test_extracted_sample_01',
        alias='12',
        individual=individual,
        volume_history=[
            {
                "date": "2020-04-15T03:50:45.127218Z",
                "update_type": "update",
                "volume_value": "0"
            }
        ],
        concentration=Decimal('0.01'),
        experimental_group=['EG01'],
        collection_site='Site1',
        container=container,
        coordinates=coordinates,
        extracted_from=extracted_from,
        volume_used=volume_used
    )


def create_individual(name, mother=None, father=None):
    return dict(
        name=name,
        taxon='Homo sapiens',
        sex='Unknown',
        mother=mother,
        father=father,
        cohort='covid-19'
    )