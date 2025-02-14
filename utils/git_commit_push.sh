#!/bin/bash

# Usage: ./utils/git_commit_push.sh "<commit_message>"

COMMIT_MESSAGE=$1
BRANCH_NAME=${GITHUB_REF_NAME}

# Ensure Git is configured
git config --global user.name "github-actions"
git config --global user.email "github-actions@github.com"

# Commit changes if there are any
if git diff --cached --quiet; then
    echo "✅ No new changes detected. Skipping commit."
    exit 0
else
    git commit -m "$COMMIT_MESSAGE"
fi

# Ensure local branch is up-to-date before pushing
if ! git pull --rebase origin "$BRANCH_NAME"; then
    echo "❌ Git rebase failed. Please resolve conflicts manually."
    exit 1  # Stop execution if rebase fails
fi

# Push after a successful rebase
git push origin "$BRANCH_NAME" || (
    echo "⚠️ Push failed. Retrying after pulling latest changes..."
    git pull --rebase origin "$BRANCH_NAME" && git push origin "$BRANCH_NAME"
)
