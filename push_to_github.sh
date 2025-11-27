#!/bin/bash
# Script to push code to GitHub repository

set -e

REPO_URL="https://github.com/FrankDidier/FacebookProj_Spider.git"

echo "=========================================="
echo "Pushing to GitHub Repository"
echo "=========================================="
echo ""
echo "Repository: $REPO_URL"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
fi

# Set remote
echo "Setting remote repository..."
git remote remove origin 2>/dev/null || true
git remote add origin "$REPO_URL"
echo "✅ Remote set to: $REPO_URL"
echo ""

# Check if .gitignore exists
if [ ! -f ".gitignore" ]; then
    echo "⚠️  Warning: .gitignore not found"
    echo "   Creating basic .gitignore..."
    cat > .gitignore << 'EOF'
venv/
dist/
build/
__pycache__/
*.pyc
.DS_Store
*.log
client_package_*/
EOF
fi

# Add all files
echo "Adding files to git..."
git add .
echo "✅ Files added"
echo ""

# Show what will be committed
echo "Files to be committed:"
git status --short | head -20
echo ""

# Commit
echo "Committing changes..."
git commit -m "Initial commit - Windows build ready with GitHub Actions" || {
    echo "⚠️  No changes to commit (or already committed)"
}
echo ""

# Set branch to main
echo "Setting branch to main..."
git branch -M main
echo "✅ Branch set to main"
echo ""

# Push
echo "=========================================="
echo "Pushing to GitHub..."
echo "=========================================="
echo ""
echo "⚠️  Note: You may need to authenticate"
echo "   - If prompted, use your GitHub username and Personal Access Token"
echo "   - Or use: git push -u origin main"
echo ""

# Try to push
if git push -u origin main 2>&1; then
    echo ""
    echo "=========================================="
    echo "✅ Successfully pushed to GitHub!"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "1. Go to: https://github.com/FrankDidier/FacebookProj_Spider"
    echo "2. Click 'Actions' tab"
    echo "3. Click 'Build Windows Executable'"
    echo "4. Click 'Run workflow' → 'Run workflow'"
    echo "5. Wait 5-10 minutes"
    echo "6. Download Windows .exe from Artifacts!"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "⚠️  Push may require authentication"
    echo "=========================================="
    echo ""
    echo "If push failed, try:"
    echo "1. Make sure repository exists on GitHub"
    echo "2. Authenticate with GitHub:"
    echo "   git push -u origin main"
    echo ""
    echo "Or use GitHub Desktop or GitHub CLI"
    echo ""
fi

