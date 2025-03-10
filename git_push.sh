#!/bin/bash

# This script safely pushes code to GitHub
# Usage: Just run ./git_push.sh (no arguments needed)

# Your GitHub information
GITHUB_USERNAME="Samplezz"
REPO_NAME="StudentResourceHub"
COMMIT_MESSAGE="fixhub"

# Add all files
git add .

# Commit changes
git commit -m "$COMMIT_MESSAGE"

# Set the remote repository if it doesn't exist
if ! git remote | grep -q "origin"; then
    # Set remote using your GitHub information
    git remote add origin "https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
else
    # Update existing remote
    git remote set-url origin "https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
fi

# Push to GitHub
git push -u origin main

echo "Code pushed successfully to https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"