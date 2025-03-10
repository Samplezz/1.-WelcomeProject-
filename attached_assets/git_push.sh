
#!/bin/bash

git init
git config user.name "${GITHUB_USERNAME}"
git config user.email "${GITHUB_USERNAME}@users.noreply.github.com"
git add .
git commit -m "Initial commit: Student Resource Portal"
git branch -M main
git remote add origin "https://${GITHUB_TOKEN}@github.com/${GITHUB_USERNAME}/student-resource-portal.git"
git push -u origin main
