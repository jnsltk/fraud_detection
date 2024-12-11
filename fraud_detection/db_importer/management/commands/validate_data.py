from django.core.management.base import BaseCommand
import subprocess
import os
from django.conf import settings
import sys


class Command(BaseCommand):
    help = "Run Great Expectations validation script"

    def handle(self, *args, **kwargs):
        # Define the path to the Anaconda Python interpreter
        anaconda_python = sys.executable
        # Moves up one level
        project_root = os.path.dirname(settings.BASE_DIR)
        validation_script = os.path.join(project_root, "great_expectations", "scripts", "validate_data.py")
        # Change the working directory to the project root
        os.chdir(project_root)

        # Run the validation script using subprocess
        try:
            result = subprocess.run(
                [anaconda_python, validation_script],
                capture_output=True,
                text=True,
            )

            # Log the output
            if result.returncode == 0:
                self.stdout.write(self.style.SUCCESS("Validation succeeded!"))
                self.stdout.write(result.stdout)
            else:
                self.stderr.write(self.style.ERROR("Validation failed!"))
                self.stderr.write(result.stderr)

        except Exception as e:
            self.stderr.write(f"An error occurred: {str(e)}")
