import pandas as pd
import json
import os
import glob
from datetime import datetime
import subprocess

# Function to convert JSON files back to Excel sheets
def json_to_excel(json_dir, output_excel_file):
    """
    Convert JSON files from a directory into an Excel file with each JSON file as a separate sheet.
    
    :param json_dir: Directory containing the JSON files
    :param output_excel_file: Path to save the resulting Excel file
    """
    # Get all JSON files in the directory
    json_files = glob.glob(os.path.join(json_dir, '*.json'))
    
    # Create an Excel writer object
    with pd.ExcelWriter(output_excel_file, engine='xlsxwriter') as writer:
        for json_file in json_files:
            # Get the sheet name from the JSON file name (without the .json extension)
            sheet_name = os.path.splitext(os.path.basename(json_file))[0]
            
            # Load the JSON data
            with open(json_file, 'r') as f:
                json_data = json.load(f)
            
            # Convert JSON data to a DataFrame
            df = pd.DataFrame(json_data)
            
            # Write DataFrame to the corresponding sheet in Excel
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"Excel file has been created at: {output_excel_file}")

# Define the directory containing the JSON files
json_directory = '../output_json'  # Replace with your directory containing JSON files

# Define the output folder
output_folder = './final-matrixify-export'  # Folder where the Excel file will be saved
os.makedirs(output_folder, exist_ok=True)  # Create the folder if it doesn't exist

# Get the current date and time to format the file name
current_time = datetime.now().strftime('%Y-%m-%d_%H%M%S')
output_excel_file = os.path.join(output_folder, f'Export_{current_time}.xlsx')  # Excel file path with dynamic name

# Call the function to convert JSON to Excel
json_to_excel(json_directory, output_excel_file)

# Ensure GITHUB_TOKEN is set up (GitHub Actions provides this automatically)
github_token = os.getenv('GITHUB_TOKEN')

# Git commands to commit and push the generated Excel file to GitHub
try:
    # Add the file to staging
    subprocess.run(['git', 'add', output_excel_file], check=True)
    
    # Commit the file with a message
    subprocess.run(['git', 'commit', '-m', f'Add Excel file {output_excel_file}'], check=True)
    
    # Push the changes to the remote repository using GITHUB_TOKEN for authentication
    push_command = [
        'git', 'push', 
        f'https://{github_token}@github.com/{os.getenv("GITHUB_REPOSITORY")}.git', 
        'main'  # Adjust branch if needed
    ]
    subprocess.run(push_command, check=True)

    print(f"Excel file pushed to GitHub successfully.")


except subprocess.CalledProcessError as e:
    print(f"Error occurred during Git operations: {e}")
