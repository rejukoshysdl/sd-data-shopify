#!/bin/bash

# Define an array of files you want to check for changes
files=("../repo-shopify-data/Pages.json" "../repo-shopify-data/Redirects.json")

# Initialize an empty string to hold the file list for git diff
file_list=""

# Loop through the files array and add each file to the git diff command
for file in "${files[@]}"; do
    file_list="$file_list $file"
done

# Run git diff on the specified files
git diff  $file_list > ../changes/git-diff/changes.diff

# Execute the Python script to generate changes
python3.13 extractIdByPage.py

# Execute the Python script to generate changes
python3.13 extract-changes-only.py

echo "Script execution completed."
