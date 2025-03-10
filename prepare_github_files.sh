#!/bin/bash

# Create a directory for GitHub export
mkdir -p github_export

# Copy core Python files
cp streamlit.py admin.py models.py utils.py github_export/

# Copy README
cp README.md github_export/

# Copy Git push script for reference
cp git_push.sh github_export/

# Copy .streamlit configuration folder
mkdir -p github_export/.streamlit
cp .streamlit/config.toml github_export/.streamlit/

# Copy data folder (excluding any large or sensitive files)
mkdir -p github_export/data
cp data/settings.json github_export/data/ 2>/dev/null || echo "No settings.json found"
cp data/requests.json github_export/data/ 2>/dev/null || echo "No requests.json found"

# Create assets directory
mkdir -p github_export/assets

# Copy images and assets
find . -maxdepth 1 -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" | xargs -I{} cp {} github_export/ 2>/dev/null || echo "No image files found in root"

# Copy any assets from assets directory
if [ -d "assets" ]; then
  find assets -type f | grep -v "__pycache__" | xargs -I{} cp {} github_export/assets/ 2>/dev/null || echo "No asset files found"
fi

# Create a .gitignore file
cat > github_export/.gitignore << EOL
__pycache__/
*.py[cod]
*$py.class
*.so
.env
.venv
env/
venv/
ENV/
.streamlit/secrets.toml
.cache/
EOL

# Create a basic requirements.txt file
cat > github_export/requirements.txt << EOL
streamlit>=1.32.0
pandas>=2.0.0
plotly>=5.18.0
pillow>=10.0.0
EOL

# Create tar archive
cd github_export
tar -czf ../StudentResourceHub.tar.gz .

echo "GitHub export files prepared successfully!"
echo "You can download StudentResourceHub.tar.gz and extract it to push to GitHub."