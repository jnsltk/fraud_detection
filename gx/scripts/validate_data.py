'''
    Made by: Shiyao Xin
'''

import json
import great_expectations as gx
import os
import sys
import shutil
from glob import glob  # For cleaning up files
from great_expectations.datasource.fluent import BatchRequest
import tempfile

def main():
    try:
        # Get the base directory from the environment variable
        base_directory = os.getenv("CSV_BASE_DIRECTORY", "/tmp")
        temp_directory = os.path.join(base_directory, "great_expectations_temp")

        # Ensure the directories exists
        os.makedirs(base_directory, exist_ok=True)
        os.makedirs(temp_directory, exist_ok=True)  
        
        # Check if a file path was provided as a command-line argument
        if len(sys.argv) < 2:
            # Create a temporary file to store the in-memory CSV input data
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", dir='/tmp') as temp_file:
                # Read the input from stdin (user-provided data) and write it to the temporary CSV file
                temp_file.write(sys.stdin.read().encode('utf-8'))
                temp_file_path = temp_file.name  # Store the path to the temporary file
            # Extract the file name from the temporary file path (used later for batch request)
            temp_file_name = os.path.basename(temp_file_path)
            expectation_suite_name = "user_input_expectation_suite"  # Use user input expectation suite
        else: 
            # If a file path is provided as an argument, treat it as an admin file input
            file_path = sys.argv[1]

            # Check whether the file exists
            if not os.path.isfile(file_path):
                print(f"File not found: {file_path}")
                sys.exit(1)

            # Copy the uploaded file temporarily to the base_directory
            temp_file_name = os.path.basename(file_path)
            temp_file_path = os.path.join(temp_directory, temp_file_name)
            # Remove the file if it already exists in /tmp
            if os.path.isfile(temp_file_path):
                os.remove(temp_file_path)
                print(f"Existing file removed: {temp_file_path}")
            shutil.copy(file_path, temp_file_path)
            expectation_suite_name = "transaction_expectation_suite"  # Use admin expectation suite

        # Initialize the Great Expectations context
        context = gx.get_context()

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
            expectation_suite_name=expectation_suite_name
        )

        # Run validation and get results
        results = validator.validate()

        # Log validation results
        if results["success"]:
            # Success path outputs consistent JSON
            print(json.dumps({"status": "success", "message": "Validation succeeded!"}))
            sys.exit(0)  # Exit with success
        else:
            failed_expectations = [
                {
                    "expectation": result["expectation_config"]["type"],  # Expectation type
                    "column": result["expectation_config"]["kwargs"].get("column"),  # Column name
                    "unexpected_count": result["result"].get("unexpected_count"),  # Count of unexpected values
                    "unexpected_percent": result["result"].get("unexpected_percent"),  # Percentage of unexpected values
                    "partial_unexpected_list": result["result"].get("partial_unexpected_list")  # Sample of unexpected values
                }
                for result in results["results"] if not result["success"]
            ]

            print(json.dumps({
                "status": "error",
                "message": "Validation failed. See details.",
                "failures": failed_expectations
            }))
            sys.exit(1)  # Exit with failure

    except Exception as e:
        print(f"Error during validation: {e}")
        sys.exit(1)
    finally:
        if os.path.isfile(temp_file_path):
            os.remove(temp_file_path)
            # print(f"Temporary file removed: {temp_file_path}")

if __name__ == "__main__":
    main()
