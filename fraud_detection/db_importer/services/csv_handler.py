import csv
import json
from io import TextIOWrapper
from json import JSONDecodeError
from logging import exception

from matplotlib.cbook import flatten

from detector.models import Transaction
import subprocess
import os
import detector.services.ml_pipeline.added_features as added_features


# ------------------------------ Data Validation ----------------------------- #
def validate_csv_data(temp_file_path):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
    try:
        # Validate the file using the Great Expectations script
        validation_script = os.path.join(project_root, "gx", "scripts", "validate_data.py")
        anaconda_python = "/opt/anaconda3/envs/prj/bin/python"

        # Check whether the file exists
        if not os.path.isfile(temp_file_path):
            raise FileNotFoundError(f"File not saved correctly: {temp_file_path}")

        print("Start data validation......")

        result = subprocess.run(
            [anaconda_python, validation_script, temp_file_path],
            capture_output=True,
            text=True,
        )
        try:
            # Parse the result
            output = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print(f"Raw output: {repr(result.stdout)}")
            return {"status": "error", "message": "Validation script returned invalid or empty output."}

        # # Check the validation result
        if result.returncode != 0:
            failure_details = "\n".join([
                f"\t- Expectation: {failure['expectation']} on column '{failure['column']}', "
                f"Unexpected Count: {failure['unexpected_count']}, "
                f"Unexpected Percent: {failure['unexpected_percent']}%, "
                f"Sample Unexpected: {failure['partial_unexpected_list']}" for failure in output.get("failures", [])
            ])
            print(
                f"\033[1;91mData validation failed! Failure details as below:\033[0m")  # Log the failure result in red
            print(f"\033[1;91m{failure_details}\033[0m")  # Log the failure details in red
            return {"status": "error", "message": f"{output['message']}\nFailures:\n{repr(result.stdout)}"}

        else:
            print(f"\033[1;92mValidation succeeded!\033[0m")  # Log the successful result in green
            return {"status": "success", "message": "Validation succeeded!"}
    except Exception as e:
        print(f"Error during validation: {e}")
        return {"status": "error", "message": f"An error occurred during validation: {str(e)}"}


# ------------------------------ Data Insertion ------------------------------ #
def process_csv(input_file):
    # Save the uploaded file temporarily for validation
    temp_file_path = "/tmp/uploaded_file.csv"

    with open(temp_file_path, "w", encoding="utf-8") as temp_file:
        data = TextIOWrapper(input_file, encoding="utf-8")
        temp_file.write(data.read())
    try:
        validation_result = validate_csv_data(temp_file_path)
        if validation_result["status"] != "success":
            return validation_result

        print("Start inserting...")
        with open(temp_file_path, "r", encoding="utf-8") as temp_file:
            reader = csv.DictReader(temp_file)
            data_to_insert = []

            # Skip first row containing headers
            # next(reader, None)

            # Stop pycharm from complaining with type hinting
            row: dict
            for row in reader:
                velocity = flatten_velocity(row, 'velocity_last_hour')
                row.update(velocity)

                if not added_features.has_currency(row['currency']):
                    raise ValueError(f"Invalid currency: {row['currency']}")

                try:
                    data_to_insert.append(Transaction(**row))
                except Exception as e:
                    print(f"Error processing row {row}: {e}")

            Transaction.objects.bulk_create(data_to_insert)
        return {"status": "success", "message": "File processed successfully!"}
    except Exception as e:
        print(f"Error during processing: {e}")
        return {"status": "error", "message": f"An error occurred during processing: {str(e)}"}
    finally:
        # Clean up the temporary file
        if os.path.isfile(temp_file_path):
            os.remove(temp_file_path)


def flatten_velocity(row, fieldname):
    json_string = row[fieldname]
    row.pop(fieldname)

    json_string = json_string.replace("'", '"')
    try:
        parsed = json.loads(json_string)
        # append v_ to the beginning of original values
        return {f"v_{key}": value for key, value in parsed.items()}
    except JSONDecodeError as e:
        print(f'Error decoding {fieldname}, {e}')
