#!/bin/bash

# Load configuration from the property file
CONFIG_FILE="../config.properties"

if [ -f "$CONFIG_FILE" ]; then
    echo "Loading configuration from $CONFIG_FILE"
    while IFS='=' read -r key value; do
        if [[ ! "$key" =~ ^# && -n "$key" ]]; then
            eval "$key=\"$value\""
        fi
    done < "$CONFIG_FILE"
else
    echo "Error: Configuration file $CONFIG_FILE not found!"
    exit 1
fi
# Function to clear a directory
clear_directory() {
    local dir=$1
    if [ -d "$dir" ]; then
        echo "Clearing directory: $dir"
        rm -rf "$dir"/*
    else
        echo "Creating directory: $dir"
        mkdir -p "$dir"
    fi
}

# Clear all required directories
clear_directory "$FINAL_OUTPUT_DIR"
clear_directory "$GIT_DIFF_DIR"
clear_directory "$ID_OUTPUT_DIR"

# Convert REPO_FILES comma-separated values into an array
IFS=', ' read -r -a files <<< "$REPO_FILES"

# Initialize an empty string to hold the file list for git diff
file_list=""

# Loop through the files array and add each file to the git diff command
for file in "${files[@]}"; do
    file_list="$file_list $file"
done

# Run git diff on the specified files
git diff  $file_list > "$DIFF_FILE"

# Execute the Python script to extract changed IDs
python3.13 extractIdByPage.py

# Execute the Python script to extract only the changes
python3.13 extract-changes-only.py

echo "Script execution completed."
