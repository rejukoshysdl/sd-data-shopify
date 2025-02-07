import json
import re

# Path to the original Pages.json file
original_file_path = '../repo-shopify-data/Pages.json'

# Path to the diff file (changes.diff)
diff_file_path = '../changes/git-diff/changes.diff'

# Save the modified pages to a new JSON file
output_file_path = '../changes/final-output/updated_pages.json'

# Load the original Pages.json data
with open(original_file_path, 'r') as file:
    pages_data = json.load(file)

# Function to extract modified blocks from the diff file
def extract_changes_from_diff(diff_file_path):
    changes = []
    
    with open(diff_file_path, 'r') as file:
        content = file.read()
        
        # Regex to match the lines for ID, Handle, and content change
        diff_blocks = re.findall(r'@@ -(\d+),(\d+) \+(\d+),(\d+) @@\n([\s\S]+?)(?=@@ |\Z)', content)
        
        for block in diff_blocks:
            start_line, num_lines, new_start, new_num_lines, diff_content = block
            # Extract all ID and Handle entries from the diff content
            ids_and_handles = re.findall(r'"ID": "([^"]+)",\s+"Handle": "([^"]+)"', diff_content)
            for id_handle in ids_and_handles:
                changes.append(id_handle)  # Store the ID and Handle of the modified block

    return changes

# Extract the changes from the diff file
changes = extract_changes_from_diff(diff_file_path)

# Filter the Pages.json data for only the modified blocks
modified_pages = []

for page in pages_data:
    for id_handle in changes:
        if page.get('ID') == id_handle[0] and page.get('Handle') == id_handle[1]:
            modified_pages.append(page)


with open(output_file_path, 'w') as file:
    json.dump(modified_pages, file, indent=4)

print(f"Modified pages written to {output_file_path}")
