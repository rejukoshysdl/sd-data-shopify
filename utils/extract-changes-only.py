import json
import os
import re

# Define paths
changed_ids_file = "../changes/id-output/changed_ids.txt"
original_files = {
    'Pages': '../repo-shopify-data/Pages.json',
    'Redirects': '../repo-shopify-data/Redirects.json'
}
output_dir = "../changes/final-output/"

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Function to load JSON data from a file
def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return []

# Function to write JSON data to a file
def write_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

# Function to read changed IDs from changed_ids.txt
def read_changed_ids(changed_ids_file):
    changed_ids = {}
    with open(changed_ids_file, "r") as file:
        for line in file:
            match = re.match(r'(\w+) -> ([\d, ]+)', line.strip())
            if match:
                section = match.group(1)
                ids = match.group(2).split(", ")
                changed_ids[section] = ids
    return changed_ids

# Read changed IDs
changed_ids = read_changed_ids(changed_ids_file)

# Dictionary to store extracted data
output_data = {}

# Process each file and extract relevant JSON blocks
for section, ids in changed_ids.items():
    if section in original_files:
        file_path = original_files[section]
        data = load_json(file_path)

        # Extract only blocks that match the changed IDs
        relevant_blocks = [block for block in data if block.get('ID') in ids]

        if relevant_blocks:
            output_data[section] = relevant_blocks
            output_file_path = os.path.join(output_dir, f"{section}.json")
            write_json(output_file_path, relevant_blocks)
            print(f"Extracted {len(relevant_blocks)} blocks for {section} and saved to {output_file_path}")

print("Extraction process completed.")
