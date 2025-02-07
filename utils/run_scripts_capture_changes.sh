#!/bin/bash 

git diff origin/dev dev > ../changes/git-diff/changes.diff 

# Execute the  Python script to generate changes
python3.13 extract-changes-only.py

echo "Script execution completed."
