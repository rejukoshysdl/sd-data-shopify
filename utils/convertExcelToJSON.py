import pandas as pd
import json
import os
import glob

# Function to exclude specific sheets
def exclude_sheet(sheet_name, excluded_sheets):
    """
    Check if the sheet name should be excluded based on a list of excluded sheets.
    
    :param sheet_name: Name of the sheet to check
    :param excluded_sheets: List of sheet names to exclude
    :return: Boolean, True if sheet is in the exclude list, False otherwise
    """
    return sheet_name in excluded_sheets

# Get the current working directory
current_dir = os.getcwd()

# Define the path to the `developer_export` folder
developer_export_dir = os.path.join(current_dir, '../developer_export')

# Find all .xlsx files in the developer_export directory
xlsx_files = glob.glob(os.path.join(developer_export_dir, '*.xlsx'))

# Check if there is exactly one .xlsx file in the directory
if len(xlsx_files) != 1:
    raise ValueError("There should be exactly one .xlsx file in the developer_export directory.")

# Use the found .xlsx file
file_path = xlsx_files[0]

# Load the Excel file
xls = pd.ExcelFile(file_path)

# Get sheet names
sheet_names = xls.sheet_names

# Define sheets to exclude (e.g., Export Summary)
excluded_sheets = ["Export Summary"]

# Create a dictionary of JSON files (one for each sheet)
json_files = {}
for sheet in sheet_names:
    # Skip the sheets that are in the excluded_sheets list
    if exclude_sheet(sheet, excluded_sheets):
        continue
    
    # Read the sheet into a DataFrame
    df = pd.read_excel(xls, sheet_name=sheet)
    
    # Replace NaN values with an empty string
    df = df.fillna("")
    
    # Convert each sheet to a list of dictionaries (JSON format)
    json_files[sheet] = df.to_dict(orient='records')

# Define the output directory for JSON files
output_dir = "../output_json"
os.makedirs(output_dir, exist_ok=True)

# Save each sheet's data as a separate JSON file
for sheet, json_data in json_files.items():
    output_file = os.path.join(output_dir, f"{sheet}.json")
    with open(output_file, 'w') as f:
        json.dump(json_data, f, indent=4)

print(f"JSON files saved to {output_dir}")
