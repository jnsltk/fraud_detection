'''
    Made by: Yingchao Ji
'''

# Split data into multiple files

import csv

def split_csv(input_file, output_prefix, rows_per_file, max_rows):
    with open(input_file, 'r') as infile:
        reader = csv.reader(infile)
        header = next(reader)  # Get the header (column names)

        file_count = 1
        rows = []
        total_rows = 0  # To count the total number of rows processed
        total_files = 0  # To count the total number of files created
        
        # Read the CSV file row by row
        for row_num, row in enumerate(reader, 1):
            # If max_rows is set and we have reached the limit, stop processing
            if max_rows is not None and total_rows >= max_rows:  
                break
            
            rows.append(row)
            total_rows += 1  # Increase total row counter

            if row_num % rows_per_file == 0:
                # Write a new file every time the specified row count is reached
                with open(f"{output_prefix}_{file_count}.csv", 'w', newline='') as outfile:
                    writer = csv.writer(outfile)
                    writer.writerow(header)  # Write the header
                    writer.writerows(rows)
                print(f"File {output_prefix}_{file_count}.csv has been written.")
                file_count += 1
                total_files += 1  # Increment the file count
                rows = []  # Reset row data
        
        # If the last chunk of data doesn't perfectly fill a file, save it as well
        if rows:
            with open(f"{output_prefix}_{file_count}.csv", 'w', newline='') as outfile:
                writer = csv.writer(outfile)
                writer.writerow(header)
                writer.writerows(rows)
            total_files += 1  # Increment the file count
            print(f"File {output_prefix}_{file_count}.csv has been written.")
        
        print(f"Total rows processed: {total_rows}")
        print(f"File has been successfully split into {total_files} files.")

input_file = 'input_file'
output_file = 'output_file'
row_number = 100000  # Each new file will contain number of rows
max_rows = None  # Set to number if has limit on total rows. Set to None if no limit on total rows. 

split_csv(input_file, output_file, row_number, max_rows)  # Call the function to split the file
