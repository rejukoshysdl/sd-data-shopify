import json
import os

# Paths to the input JSON files and output file
output_json_path = '../output_json/products.json'  # File generated from the script
repo_json_path = '../repo-shopify-data/products.json'  # Source of truth file

# Load the output JSON file (from the newly exported data)
with open(output_json_path, 'r') as output_file:
    output_json = json.load(output_file)

# Load the repo JSON file (the source of truth)
with open(repo_json_path, 'r') as repo_file:
    repo_json = json.load(repo_file)

# Create a dictionary for faster lookup by Handle from the output JSON
output_dict = {product['Handle']: product for product in output_json}
repo_dict = {product['Handle']: product for product in repo_json}

# List to store the final merged products
merged_products = []

# 1. Loop through products in output_json and merge them into repo_json
for product in output_json:
    # Replace the corresponding product in repo_json based on the Handle
    repo_dict[product['Handle']] = product

# 2. Loop through products in repo_json and mark those that are not in output_json for deletion
for product_handle, product in repo_dict.items():
    if product_handle not in output_dict:
        # If product is not in the output JSON, mark it for deletion
        product['Command'] = 'DELETE'
    
    # Add to the merged products list
    merged_products.append(product)

# Save the merged data back to repo-shopify-data/products.json
with open(repo_json_path, 'w') as output_file:
    json.dump(merged_products, output_file, indent=4)

print(f"Products successfully merged and saved to {repo_json_path}")
