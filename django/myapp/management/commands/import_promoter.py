from django.core.management.base import BaseCommand
import csv
from myapp.models import PromoterRecord


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
                        score=row["score"],
                        density=row["density"],
                        sequence=row["sequence"],
                        annotation=row["annotation"],
                        score_norm=row["score_norm"],
                        density_norm=row["density_norm"],
                        combined=row["combined"],
                        tier=row["tier"],
                        t1=row["t1"],
                        t2=row["t2"],
                        group=row["new_group"],
                        bacterium_name_formatted=row["bacterium_name_formatted"],
                        assembly=row["assembly"],
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