import os
import re
import subprocess

# Detect if running in GitHub Actions
GITHUB_WORKSPACE = os.getenv("GITHUB_WORKSPACE", os.getcwd())  # Use GitHub workspace if available

# Paths for input and output files
diff_file_path = os.path.join(GITHUB_WORKSPACE, "changes/git-diff/changes.diff")
output_folder = os.path.join(GITHUB_WORKSPACE, "changes/id-output")
output_file_path = os.path.join(output_folder, "changed_ids.txt")

# Ensure the output directory exists
os.makedirs(output_folder, exist_ok=True)

# Dictionary to store extracted IDs grouped by section (Pages, Redirects, Files, etc.)
changed_ids = {}

# Regular expressions for parsing the diff file
section_pattern = re.compile(r'^diff --git a/repo-shopify-data/([\w-]+)\.json')
id_pattern = re.compile(r'"ID":\s*"([^"]+)"')  # Capture numeric and GID formats
change_block_pattern = re.compile(r'^@@')

# Initialize variables
current_section = None
inside_change_block = False

# Ensure diff file exists before processing
if not os.path.exists(diff_file_path):
    print(f"❌ Error: Diff file not found at {diff_file_path}")
    exit(1)

# Read and process the diff file
with open(diff_file_path, "r", encoding="utf-8") as file:
    for line in file:
        # Detect section (e.g., Pages.json, Redirects.json, Files.json, etc.)
        section_match = section_pattern.search(line)
        if section_match:
            current_section = section_match.group(1)
            if current_section not in changed_ids:
                changed_ids[current_section] = set()
            inside_change_block = False  # Reset when a new section starts

        # Detect start of a change block
        if change_block_pattern.search(line):
            inside_change_block = True  # Mark that we're inside a change block

        # Extract the first ID after an @@ block
        elif inside_change_block:
            id_match = id_pattern.search(line)
            if id_match:
                changed_ids[current_section].add(id_match.group(1))  # Capture GID format as well
                inside_change_block = False  # Stop looking for an ID until the next @@ block

# Remove empty sections
changed_ids = {section: list(ids) for section, ids in changed_ids.items() if ids}

# Write the extracted IDs to `changed_ids.txt`
with open(output_file_path, "w", encoding="utf-8") as output_file:
    for section, ids in changed_ids.items():
        output_file.write(f"{section} -> {', '.join(ids)}\n")

print(f"✅ Output saved to {output_file_path}")

# ** Ensure Git Tracks the File in the Repository **
try:
    subprocess.run(["git", "config", "--global", "user.name", "github-actions"], check=True)
    subprocess.run(["git", "config", "--global", "user.email", "github-actions@github.com"], check=True)

    # ** Check if there are local changes before stashing **
    has_changes = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout.strip()
    if has_changes:
        print("🔄 Stashing local changes before pulling...")
        subprocess.run(["git", "stash", "push", "-m", "Saving unstaged changes before pull"], check=True)
        stash_created = True
    else:
        print("✅ No local changes to stash.")
        stash_created = False

    # ** Fetch latest branch to avoid non-fast-forward issues **
    subprocess.run(["git", "fetch", "origin", "int"], check=True)
    subprocess.run(["git", "checkout", "int"], check=True)
    subprocess.run(["git", "pull", "--rebase", "origin", "int"], check=True)

    # ** Only pop stash if one was created earlier **
    if stash_created:
        print("🔄 Restoring stashed changes...")
        subprocess.run(["git", "stash", "pop"], check=True)
    else:
        print("✅ No stash to apply.")

    # ** Add extracted IDs file and push to remote repository **
    subprocess.run(["git", "add", output_file_path], check=True)
    subprocess.run(["git", "status"], check=True)

    # ** Prevent empty commits **
    if subprocess.run(["git", "diff", "--cached", "--quiet"]).returncode == 0:
        print("✅ No new changes detected. Skipping commit.")
    else:
        subprocess.run(["git", "commit", "-m", "Add extracted changed IDs"], check=True)

        # ** Attempt push, retry with force if needed **
        if subprocess.run(["git", "push", "origin", "int"]).returncode != 0:
            print("⚠️ Warning: Push failed. Retrying with force...")
            subprocess.run(["git", "push", "origin", "int", "--force"], check=True)

    print("✅ Extracted IDs file pushed to GitHub successfully.")

except subprocess.CalledProcessError as e:
    print(f"❌ Error during Git operations: {e}")
