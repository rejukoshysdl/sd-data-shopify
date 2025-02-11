import json
import os
import glob
import pandas as pd
from datetime import datetime
import subprocess

# Function to convert JSON files from a directory into an Excel file
def json_to_excel(json_dir, output_folder):
    """
    Convert JSON files from a directory into an Excel file with each JSON file as a separate sheet.

    :param json_dir: Directory containing the JSON files (including subdirectories)
    :param output_folder: Folder where the Excel file will be saved
    """
    print(f"🔍 Searching for JSON files in: {os.path.abspath(json_dir)}")

    # Get all JSON files recursively
    json_files = glob.glob(os.path.join(json_dir, '**', '*.json'), recursive=True)

    if not json_files:
        print(f"🚫 Skipping {json_dir} (No JSON files found).")
        return None

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Generate unique Excel file name
    current_time = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    output_excel_file = os.path.join(output_folder, f'Export_{current_time}.xlsx')

    print(f"📄 Processing {len(json_files)} JSON files in {json_dir}...")

    # Create an Excel writer object
    with pd.ExcelWriter(output_excel_file, engine='xlsxwriter') as writer:
        for json_file in json_files:
            # Extract sheet name from JSON file name (max length = 31 for Excel sheets)
            sheet_name = os.path.splitext(os.path.basename(json_file))[0][:31]

            # Load JSON data
            with open(json_file, 'r') as f:
                json_data = json.load(f)

            print(f"✅ Processing file: {json_file}")

            # Convert JSON to DataFrame
            df = pd.DataFrame(json_data)

            # Handle boolean and numeric formatting
            for col in df.columns:
                if pd.api.types.is_bool_dtype(df[col]):
                    df[col] = df[col].replace({True: 'TRUE', False: 'FALSE'})
                elif pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) and x == int(x) else f"{x:,.2f}")

            # Write DataFrame to corresponding sheet
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"🎉 Excel file created: {output_excel_file}")

    return output_excel_file  # Return the file path for GitHub push

# Define JSON directories and corresponding Excel export folders
folder_mappings = {
    "repo-shopify-data": "final-matrixify-export",
    "changes/change-only-jsons": "changes/change-only-excel"
}

# List to store generated Excel file paths
generated_files = []

# Process each JSON directory
for json_dir, output_dir in folder_mappings.items():
    print(f"\n🚀 Processing directory: {json_dir} → {output_dir}")
    excel_file = json_to_excel(json_dir, output_dir)
    if excel_file:
        generated_files.append(excel_file)

# GitHub push logic
github_token = os.getenv('GITHUB_TOKEN')
branch_name = os.getenv('GITHUB_REF_NAME', 'main')  # Default to 'main'

print(f"\n🔹 Using GitHub branch: {branch_name}")

try:
    for file_path in generated_files:
        # Add the file to Git staging
        subprocess.run(['git', 'add', file_path], check=True)

        # Commit the file with a message
        subprocess.run(['git', 'commit', '-m', f'Add Excel file {file_path}'], check=True)

        # Push to GitHub using GITHUB_TOKEN
        push_command = [
            'git', 'push',
            f'https://{github_token}@github.com/{os.getenv("GITHUB_REPOSITORY")}.git',
            branch_name
        ]
        subprocess.run(push_command, check=True)

    print("✅ All Excel files pushed to GitHub successfully.")

except subprocess.CalledProcessError as e:
    print(f"❌ Error during Git operations: {e}")

print("\n🎯 Script execution completed!")
