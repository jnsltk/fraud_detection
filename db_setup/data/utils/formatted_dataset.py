# Formatted data
# Replace single quotes in JSON format with double quotes
# Delete duplicate transaction_id data

import csv
import json

input_file = 'C:/Users/VidaStone/Downloads/archive/synthetic_fraud_data_1.csv'
output_file = 'C:/Users/VidaStone/Downloads/archive/synthetic_fraud_data_1_formatted.csv'

# Function: Replace single quotes with double quotes to ensure the data is in JSON format
def convert_to_json_format(data):
    # If the data looks like a JSON string (surrounded by single quotes), replace single quotes with double quotes
    try:
        # Try to parse the data as JSON
        json.loads(data)  # If it's valid JSON, return it as is
        return data
    except json.JSONDecodeError:
        # If parsing fails (i.e., it's not valid JSON), replace single quotes with double quotes
        return data.replace("'", '"')

# A set to store processed transaction_ids to prevent duplicates
seen_transaction_ids = set()

# Open the input and output files
with open(input_file, 'r', newline='', encoding='utf-8') as infile, \
     open(output_file, 'w', newline='', encoding='utf-8') as outfile:

    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    
    # Write the header (if present)
    header = next(reader)
    writer.writerow(header)
    
    for row in reader:
        transaction_id = row[0]  # Assuming the transaction_id is the first column

        # Check if this transaction_id has been processed before
        if transaction_id not in seen_transaction_ids:
            # If not processed, mark it as seen and continue processing
            seen_transaction_ids.add(transaction_id)

            # Process columns that need to be converted to JSON format
            for i, value in enumerate(row):
                row[i] = convert_to_json_format(value)
            
            # Write the processed row to the output file
            writer.writerow(row)

print(f"File {input_file}.csv has been processed.")