from datetime import datetime, timezone, timedelta
from django.core.management.base import BaseCommand
import os
import sys
from detector.models import FraudDetectionModel
from django.db.models import Value
from django.db.models import Max
from detector.services.ml_pipeline import make_model


class Command(BaseCommand):
    help = "Creates a new model if needed"

    def handle(self, *args, **kwargs):

        # Gets the version from the docker environment, set by the CI/CD pipeline
        version_tag = os.environ.get('VERSION_TAG')
        new_major_version = version_tag.split('.')[0]

        # Get the last model version from the database
        last_model = FraudDetectionModel.objects.aggregate(max_version=Max('version'))
        last_model_major_version = last_model.get('max_version').split('.')[0][1:]

        # Prints the versions for debugging
        print(f"new major version is: {new_major_version}")
        print(f"last model major version is: {last_model_major_version}")

        # If the major version is different, train a new model
        if last_model_major_version != new_major_version:
            print("Training new model...")
            self.create_model(f'v{new_major_version}.0')

    def create_model(self, version):
        temp_file_path = "/tmp/tmp_model.keras"

        # Call the make_model function from the ml_pipeline service
        result = make_model()

        # Save the model to a temporary file
        result.model.save(temp_file_path)

        # Read model file
        with open(temp_file_path, 'rb') as f:
            model_bin = f.read()

        # Save the model to the database
        model = FraudDetectionModel(version=version,
                                    date_created=datetime.now(),
                                    created_by=None,
                                    dataset_size=result.true_sample_size,
                                    training_data_start_date=datetime.fromtimestamp(0, tz=timezone.utc),
                                    training_data_end_date=datetime.now() + timedelta(days=1),
                                    score=result.test_result['weighted avg']['f1-score'],
                                    detailed_performance=result.test_result,
                                    metadata=result.metadata,
                                    model_file=model_bin,
                                    is_deployed=False)
        model.save()
