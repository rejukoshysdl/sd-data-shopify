import re
import os
import shutil

# Path to the changes.diff file
diff_file_path = "../changes/git-diff/changes.diff"  # Update the path if needed
output_folder = "../changes/id-output"  # Destination folder for the output file
output_file_path = os.path.join(output_folder, "changed_ids.txt")

# Ensure the output directory exists
os.makedirs(output_folder, exist_ok=True)

# Dictionary to store extracted IDs grouped by section (Pages, Redirects, Files, etc.)
changed_ids = {}

# Regular expressions
section_pattern = re.compile(r'^diff --git a/repo-shopify-data/(\w+)\.json')
id_pattern = re.compile(r'"ID":\s*"([^"]+)"')  # Updated to capture both numeric and GID formats
change_block_pattern = re.compile(r'^@@')

# Initialize variables
current_section = None
inside_change_block = False

# Read and process the diff file
with open(diff_file_path, "r") as file:
    for line in file:
        # Detect section (e.g., Pages.json, Redirects.json, Files.json, etc.)
        section_match = section_pattern.search(line)
        if section_match:
            current_section = section_match.group(1)
            if current_section not in changed_ids:
                changed_ids[current_section] = set()
            inside_change_block = False  # Reset when a new section starts

        # Detect start of a change block
        if change_block_pattern.search(line):
            inside_change_block = True  # Mark that we're inside a change block

        # Extract the first ID after an @@ block
        elif inside_change_block:
            id_match = id_pattern.search(line)
            if id_match:
                changed_ids[current_section].add(id_match.group(1))  # Capture GID format as well
                inside_change_block = False  # Stop looking for an ID until the next @@ block

# Remove empty sections
changed_ids = {section: list(ids) for section, ids in changed_ids.items() if ids}

# Write the IDs to a file
with open(output_file_path, "w") as output_file:
    for section, ids in changed_ids.items():
        output_file.write(f"{section} -> {', '.join(ids)}\n")

print(f"Output saved to {output_file_path}")
