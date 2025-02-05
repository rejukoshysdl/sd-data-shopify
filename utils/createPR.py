import json
import os
import glob

# Paths to the output and repo directories
output_json_dir = '../output_json'  # Directory containing the JSON files generated from the script
repo_json_dir = '../repo-shopify-data'  # Source of truth directory

# Get all JSON files in the output directory
output_json_files = glob.glob(os.path.join(output_json_dir, '*.json'))

# Process each JSON file
for output_json_path in output_json_files:
    # Derive the corresponding repo file path from the output path
    file_name = os.path.basename(output_json_path)
    repo_json_path = os.path.join(repo_json_dir, file_name)
    
    if not os.path.exists(repo_json_path):
        print(f"Warning: {repo_json_path} does not exist, skipping file.")
        continue

    # Load the output JSON file (from the newly exported data)
    with open(output_json_path, 'r') as output_file:
        output_json = json.load(output_file)

    # Load the repo JSON file (the source of truth)
    with open(repo_json_path, 'r') as repo_file:
        repo_json = json.load(repo_file)

    # Create a dictionary for faster lookup
    if file_name == "Files.json" or file_name == "Redirects.json":
        # Use 'ID' as the key for Files.json and Redirects.json
        output_dict = {item['ID']: item for item in output_json if 'ID' in item}
        repo_dict = {item['ID']: item for item in repo_json if 'ID' in item}
    else:
        # Use 'Handle' as the key for other JSON files
        output_dict = {item['Handle']: item for item in output_json if 'Handle' in item}
        repo_dict = {item['Handle']: item for item in repo_json if 'Handle' in item}

    # List to store the final merged items
    merged_items = []

    # 1. Loop through items in output_json and merge them into repo_json
    for item in output_json:
        if 'ID' in item:  # Check if 'ID' exists, for Files.json and Redirects.json
            repo_dict[item['ID']] = item
        elif 'Handle' in item:  # For other JSON files
            repo_dict[item['Handle']] = item

    # 2. Loop through items in repo_json and mark those that are not in output_json for deletion
    for item_id_or_handle, item in repo_dict.items():
        if item_id_or_handle not in output_dict:
            # If item is not in the output JSON, mark it for deletion
            item['Command'] = 'DELETE'
        
        # Add to the merged items list
        merged_items.append(item)

    # Save the merged data back to the corresponding repo JSON file
    with open(repo_json_path, 'w') as output_file:
        json.dump(merged_items, output_file, indent=4)

    print(f"Successfully merged and saved {file_name} to {repo_json_path}")
