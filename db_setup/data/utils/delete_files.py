'''
    Made by: Yingchao Ji
'''

# Delete multiple files for quick delete

import os

def delete_files_with_prefix(directory, prefix):
    # Iterate over all files in the directory
    for file in os.listdir(directory):
        # Check if the filename contains the specified prefix
        if prefix in file:
            file_path = os.path.join(directory, file)
            try:
                os.remove(file_path)  # Delete the file
                print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")


folder_path = 'folder_path'
prefix = 'prefix_words' # Files containing the prefix

delete_files_with_prefix(folder_path, prefix) # Call the function to delete files
