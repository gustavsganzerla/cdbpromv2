from rest_framework import serializers


class PredictRequestSerializer(serializers.Serializer):
    fasta = serializers.CharField(
        help_text="DNA sequence in FASTA format."
    )


class PredictResponseSerializer(serializers.Serializer):
    prediction = serializers.CharField()
    probability = serializers.FloatField()
    model = serializers.CharField()



    