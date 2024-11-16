# Split data into multiple files

import csv

def split_csv(input_file, output_prefix, rows_per_file):
    with open(input_file, 'r') as infile:
        reader = csv.reader(infile)
        header = next(reader)  # Get the header (column names)

        file_count = 1
        rows = []
        
        # Read the CSV file row by row
        for row_num, row in enumerate(reader, 1):
            rows.append(row)
            if row_num % rows_per_file == 0:
                # Write a new file every time the specified row count is reached
                with open(f"{output_prefix}_{file_count}.csv", 'w', newline='') as outfile:
                    writer = csv.writer(outfile)
                    writer.writerow(header)  # Write the header
                    writer.writerows(rows)
                file_count += 1
                rows = []  # Reset row data
        
        # If the last chunk of data doesn't perfectly fill a file, save it as well
        if rows:
            with open(f"{output_prefix}_{file_count}.csv", 'w', newline='') as outfile:
                writer = csv.writer(outfile)
                writer.writerow(header)
                writer.writerows(rows)

input_file = 'input_file_path' # Input file path
output_file = 'output_file_path' # Output file path
row_number = 100000 # Each new file will contain number of rows of data

# Call the function to split the file
split_csv(input_file, output_file, row_number)