import json
import re
import os

# Define the paths to the original JSON files and output directory
original_files = {
    'Pages.json': '../repo-shopify-data/Pages.json',
    'Redirects.json': '../repo-shopify-data/Redirects.json'
}

# Path to the diff file (changes.diff)
diff_file_path = '../changes/git-diff/changes.diff'

# Output directory for modified files
output_dir = '../changes/final-output/'

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Function to extract modified blocks from the diff file
def extract_changes_from_diff(diff_file_path, valid_files):
    changes = {file: [] for file in valid_files}
    
    with open(diff_file_path, 'r') as file:
        content = file.read()
        
        # Regex to match the lines for ID, Handle, and content change
        diff_blocks = re.findall(r'@@ -(\d+),(\d+) \+(\d+),(\d+) @@\n([\s\S]+?)(?=@@ |\Z)', content)
        
        print("Diff blocks extracted:")
        for block in diff_blocks:
            print(block)
        
        for block in diff_blocks:
            start_line, num_lines, new_start, new_num_lines, diff_content = block
            
            # Extract the file name from the diff content (e.g., Pages.json, Redirects.json)
            file_name_match = re.match(r'--- a/([^ ]+)', diff_content)
            if file_name_match:
                file_name = file_name_match.group(1)
                if file_name in valid_files:
                    # Extract all ID and Handle entries from the diff content
                    ids_and_handles = re.findall(r'"ID": "([^"]+)",\s+"Handle": "([^"]+)"', diff_content)
                    for id_handle in ids_and_handles:
                        changes[file_name].append(id_handle)  # Store the ID and Handle of the modified block
                        
    print(f"Changes extracted: {changes}")
    return changes

# Extract the changes from the diff file for the valid files (Pages.json, Redirects.json)
valid_files = ['Pages.json', 'Redirects.json']
changes = extract_changes_from_diff(diff_file_path, valid_files)

# Function to filter and write modified data for each file
def filter_and_write_modified_data(original_files, changes, output_dir):
    for file_name, file_path in original_files.items():
        # Skip files that don't have changes
        if file_name not in changes or not changes[file_name]:
            print(f"No changes for {file_name}, skipping file.")
            continue

        # Load the original data
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Filter the modified entries based on ID and Handle
        modified_data = [
            entry for entry in data if any(
                entry.get('ID') == change[0] and entry.get('Handle') == change[1]
                for change in changes[file_name]
            )
        ]
        
        print(f"Modified data for {file_name}: {modified_data}")

        # If no modified data found, skip writing the file
        if not modified_data:
            print(f"No modified data for {file_name}, skipping write.")
            continue

        # Write the modified data to a new JSON file in the output directory
        output_file_path = os.path.join(output_dir, file_name)
        with open(output_file_path, 'w') as file:
            json.dump(modified_data, file, indent=4)

        print(f"Modified {file_name} written to {output_file_path}")

# Filter and write the modified data for Pages.json and Redirects.json
filter_and_write_modified_data(original_files, changes, output_dir)
