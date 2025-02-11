import re
import os
import shutil

# Detect GitHub workspace for remote execution
GITHUB_WORKSPACE = os.getenv("GITHUB_WORKSPACE", os.getcwd())

# Define paths
diff_file_path = os.path.join(GITHUB_WORKSPACE, "changes/git-diff/changes.diff")
output_folder = os.path.join(GITHUB_WORKSPACE, "changes/id-output")
output_file_path = os.path.join(output_folder, "changed_ids.txt")

# Ensure the output directory exists
os.makedirs(output_folder, exist_ok=True)

# Dictionary to store extracted IDs grouped by section
changed_ids = {}

# Regular expressions
section_pattern = re.compile(r'^diff --git a/repo-shopify-data/(\w+)\.json')
id_pattern = re.compile(r'"ID":\s*"([^"]+)"')
change_block_pattern = re.compile(r'^@@')

# Initialize variables
current_section = None
inside_change_block = False

# Read and process the diff file
with open(diff_file_path, "r") as file:
    for line in file:
        section_match = section_pattern.search(line)
        if section_match:
            current_section = section_match.group(1)
            if current_section not in changed_ids:
                changed_ids[current_section] = set()
            inside_change_block = False  

        if change_block_pattern.search(line):
            inside_change_block = True  

        elif inside_change_block:
            id_match = id_pattern.search(line)
            if id_match:
                changed_ids[current_section].add(id_match.group(1))  
                inside_change_block = False  

# Remove empty sections and write output
changed_ids = {section: list(ids) for section, ids in changed_ids.items() if ids}
with open(output_file_path, "w") as output_file:
    for section, ids in changed_ids.items():
        output_file.write(f"{section} -> {', '.join(ids)}\n")

print(f"✅ Output saved to {output_file_path}")
