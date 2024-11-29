import time
import great_expectations as gx
import os
import sys
import shutil
from glob import glob  # For cleaning up files
from great_expectations.datasource.fluent import BatchRequest

def main():
    # Take file path from command-line arguments
    if len(sys.argv) < 2:
        print("Usage: validate_data.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    # Check whether the file exists
    if not os.path.isfile(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)

    # Initialize the Great Expectations context
    context = gx.get_context()

    try:
        # Get the base directory from the environment variable
        base_directory = os.getenv("CSV_BASE_DIRECTORY", "/tmp")
        temp_directory = os.path.join(base_directory, "great_expectations_temp")

        # Ensure the directories exists
        os.makedirs(base_directory, exist_ok=True)
        os.makedirs(temp_directory, exist_ok=True)  

        # Copy the uploaded file temporarily to the base_directory
        temp_file_name = os.path.basename(file_path)
        temp_file_path = os.path.join(temp_directory, temp_file_name)

        # Remove the file if it already exists in /tmp
        if os.path.isfile(temp_file_path):
            os.remove(temp_file_path)
            print(f"Existing file removed: {temp_file_path}")

        shutil.copy(file_path, temp_file_path)

        data_source_name = "dataset_sample.csv"
        data_asset_name = "transaction_csv_file"

        # Define a batch dynamically
        batch_request = BatchRequest(
            datasource_name=data_source_name,
            data_asset_name=data_asset_name,
            options={"path": temp_file_name},  # Dynamically specify the file path
        )

        # Retrieve the batch dynamically
        validator = context.get_validator(
            batch_request=batch_request,
            expectation_suite_name="transaction_expectation_suite" 
        )

        # Run validation and get results
        results = validator.validate()

        # Log validation results
        if results["success"]:
            print("Validation completed: succeeded!")
            sys.exit(0)  # Exit with success
        else:
            print("Validation completed: failed!")
            print(results)
            sys.exit(1)  # Exit with failure

    except Exception as e:
        print(f"Error during validation: {e}")
        sys.exit(1)
    finally:
        if os.path.isfile(temp_file_path):
            os.remove(temp_file_path)
            print(f"Temporary file removed: {temp_file_path}")

if __name__ == "__main__":
    main()
