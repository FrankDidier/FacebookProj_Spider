#!/bin/bash
# Quick setup script for GitHub Actions Windows build

echo "=========================================="
echo "GitHub Actions Windows Build Setup"
echo "=========================================="
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    echo "✅ Git repository initialized"
    echo ""
fi

# Check if .gitignore exists
if [ ! -f ".gitignore" ]; then
    echo "Creating .gitignore..."
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
    echo "✅ .gitignore created"
    echo ""
fi

# Check if GitHub Actions workflow exists
if [ -f ".github/workflows/build-windows.yml" ]; then
    echo "✅ GitHub Actions workflow already exists"
    echo ""
else
    echo "⚠️  Warning: GitHub Actions workflow not found"
    echo "   Make sure .github/workflows/build-windows.yml exists"
    echo ""
fi

# Check git status
echo "Current git status:"
git status --short | head -10
echo ""

# Instructions
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo ""
echo "1. Create GitHub repository:"
echo "   - Go to: https://github.com/new"
echo "   - Name it (e.g., 'facebook-marketing-tool')"
echo "   - Make it PRIVATE (to protect your code)"
echo "   - Don't initialize with README"
echo ""
echo "2. Add remote and push:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git"
echo "   git add ."
echo "   git commit -m 'Initial commit - Windows build ready'"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Build Windows executable:"
echo "   - Go to: https://github.com/YOUR_USERNAME/REPO_NAME/actions"
echo "   - Click 'Build Windows Executable'"
echo "   - Click 'Run workflow' → 'Run workflow'"
echo "   - Wait 5-10 minutes"
echo "   - Download the Windows .exe from Artifacts!"
echo ""
echo "✅ That's it! No Windows PC needed!"
echo ""

