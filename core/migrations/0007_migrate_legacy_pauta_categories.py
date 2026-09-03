from django.db import migrations


def copy_legacy_categories(apps, schema_editor):
    Pauta = apps.get_model('core', 'Pauta')
    for pauta in Pauta.objects.exclude(categoria_id=None).iterator():
        pauta.categorias.add(pauta.categoria_id)


def reverse_copy_legacy_categories(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0006_pauta_categorias_pauta_edad_max_pauta_edad_min'),
    ]

    operations = [
        migrations.RunPython(copy_legacy_categories, reverse_copy_legacy_categories),
    ]
