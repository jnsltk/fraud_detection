from django.core.management.base import BaseCommand
import os
import sys
from detector.models import FraudDetectionModel
from django.db.models import Value
from django.db.models import Max


class Command(BaseCommand):
    help = "Creates a new model if needed"

    def handle(self, *args, **kwargs):
        version_tag = os.environ.get('VERSION_TAG')
        new_major_version = version_tag.split('.')[0]

        last_model = FraudDetectionModel.objects.aggregate(max_version=Max('version'))
        last_model_major_version = last_model.get('max_version').split('.')[0][1:]

        print(f"new major version is: {new_major_version}")
        print(f"last model major version is: {last_model_major_version}")

        if last_model_major_version != new_major_version:
            print("Jessie, we need to train a model!")
