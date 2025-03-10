#!/bin/bash

# This script safely pushes code to GitHub
# Usage: ./git_push.sh <github_username> <repo_name> <commit_message>

# Check if all arguments are provided
if [ $# -lt 3 ]; then
    echo "Usage: ./git_push.sh <github_username> <repo_name> <commit_message>"
    exit 1
fi

GITHUB_USERNAME="$1"
REPO_NAME="$2"
COMMIT_MESSAGE="$3"

# Add all files
git add .

# Commit changes
git commit -m "$COMMIT_MESSAGE"

# Set the remote repository if it doesn't exist
if ! git remote | grep -q "origin"; then
    # Use environment variable for token, avoiding exposing it in command line
    git remote add origin "https://${GITHUB_TOKEN}@github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
else
    # Update existing remote with token
    git remote set-url origin "https://${GITHUB_TOKEN}@github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
fi

# Push to GitHub
git push -u origin main

echo "Code pushed successfully to https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"