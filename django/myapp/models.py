from django.db import models

# Create your models here.
class PromoterRecord(models.Model):

    #bacterium,score,sequence,annotation,iso_calibrated_probability,merge_key,assembly,group,strain,asm

    bacterium = models.CharField(max_length=255, db_index=True)
    raw_score = models.FloatField()
    sequence = models.TextField()
    annotation = models.TextField()
    iso_calibrated_probability = models.FloatField()
    bacterium_name_formatted = models.CharField(max_length=255, db_index=True)
    assembly = models.CharField(max_length=255, null=True, blank=True)
    group = models.CharField(max_length=50, db_index=True)
    strain = models.CharField(max_length=255, null=True, blank=True)
    

