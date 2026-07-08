from django.core.management.base import BaseCommand
import csv
from myapp.models import PromoterRecord

'''
DB schema
    bacterium = models.CharField(max_length=255, db_index=True)
    raw_score = models.FloatField()
    sequence = models.TextField()
    annotation = models.TextField()
    iso_calibrated_probability = models.FloatField()
    bacterium_name_formatted = models.CharField(max_length=255, db_index=True)
    assembly = models.CharField(max_length=255, null=True, blank=True)
    group = models.CharField(max_length=50, db_index=True)
    strain = models.CharField(max_length=255, null=True, blank=True)

    df columns bacterium,score,sequence,annotation,iso_calibrated_probability,merge_key,assembly,group,strain,asm

'''

class Command(BaseCommand):
    help = "Import bacteria dataset from CSV"
    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str)
    def handle(self, *args, **options):
        file_path = options["file_path"]
        batch = []
        batch_size = 5000
        self.stdout.write("Starting import...")
        with open(file_path, "r") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                batch.append(
                    PromoterRecord(
                        bacterium=row["bacterium"],
                        raw_score=row["raw_score"],
                        sequence=row["sequence"],
                        annotation=row["annotation"],
                        iso_calibrated_probability=row["iso_calibrated_probability"],
                        bacterium_name_formatted=row["bacterium_name_formatted"],
                        assembly=row["assembly"],
                        group=row["group"],
                        strain=row["strain"],
                    )
                )
                #bacterium_name_formatted

                if len(batch) >= batch_size:
                    PromoterRecord.objects.bulk_create(batch, batch_size=batch_size)
                    batch = []

                if i % 10000 == 0:
                    self.stdout.write(f"Processed {i} rows")

        if batch:
            PromoterRecord.objects.bulk_create(batch, batch_size=batch_size)

        self.stdout.write(self.style.SUCCESS("Import completed"))