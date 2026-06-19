from django.db import models

# Create your models here.
class PromoterRecord(models.Model):
    bacterium = models.CharField(max_length=255, db_index=True)
    bacterium_name_formatted = models.CharField(max_length=255, db_index=True)

    assembly = models.CharField(max_length=255, db_index=True)

    sequence = models.TextField()  # large field, NOT indexed
    annotation = models.TextField(null=True, blank=True)

    score = models.FloatField()
    density = models.FloatField()
    score_norm = models.FloatField()
    density_norm = models.FloatField()
    combined = models.FloatField()

    tier = models.CharField(max_length=50, db_index=True)
    t1 = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    t2 = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    group = models.CharField(max_length=50, db_index=True)