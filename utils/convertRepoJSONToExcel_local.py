import pandas as pd
import json
import os
from datetime import datetime

# Function to convert repository JSON files back to Excel sheets for developer import
def json_to_excel(json_dir, output_excel_file):
    """
    Convert JSON files from a directory into an Excel file with each JSON file as a separate sheet.
    
    :param json_dir: Directory containing the JSON files
    :param output_excel_file: Path to save the resulting Excel file
    """
    json_files = glob.glob(os.path.join(json_dir, '*.json'))  # Get all JSON files in the directory
    
    # Create an Excel writer object to output to an Excel file
    with pd.ExcelWriter(output_excel_file, engine='xlsxwriter') as writer:
        for json_file in json_files:
            # Extract the sheet name from the JSON file name
            sheet_name = os.path.splitext(os.path.basename(json_file))[0]
            
            # Load JSON data
            with open(json_file, 'r') as f:
                json_data = json.load(f)

            # Convert the JSON data to a DataFrame
            df = pd.DataFrame(json_data)

            # Write DataFrame to the corresponding sheet in Excel
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"Sheet '{sheet_name}' saved to Excel with column order preserved.")

    print(f"Excel file has been created at: {output_excel_file}")

# Example usage
json_directory = './output_json'  # Path to the JSON files
output_excel_file = './final-matrixify-export/Export_2025-01-27.xlsx'  # Path to the output Excel file

json_to_excel(json_directory, output_excel_file)
