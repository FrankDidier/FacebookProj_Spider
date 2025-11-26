# ⚡ Quick Windows Build Guide

## 🎯 You Don't Have Windows? No Problem!

## ✅ Easiest Solution: GitHub Actions (5 minutes setup)

### What You Need:
- ✅ GitHub account (free)
- ✅ 5 minutes
- ✅ Internet connection

### Steps:

1. **Create GitHub repo** (2 min)
   ```bash
   cd /Users/vv/Desktop/src-facebook
   git init
   git add .
   git commit -m "Ready for Windows build"
   # Create repo on GitHub, then:
   git remote add origin https://github.com/YOUR_USERNAME/repo-name.git
   git push -u origin main
   ```

2. **Go to Actions tab** (1 min)
   - Click "Actions" in your GitHub repo
   - Click "Build Windows Executable"
   - Click "Run workflow" → "Run workflow"

3. **Wait 5-10 minutes** ⏱️
   - GitHub builds your Windows `.exe` automatically

4. **Download** (1 min)
   - Click on completed workflow
   - Download "FacebookMarketingTool-Windows-Package"
   - You have your `.exe`! 🎉

## 📦 Alternative: Virtual Machine

If you prefer local control:

1. **Install VirtualBox** (free)
   - https://www.virtualbox.org

2. **Download Windows 11 ISO** (free evaluation)
   - https://www.microsoft.com/software-download/windows11

3. **Create VM & Install Windows** (~30 min setup)

4. **Build in VM**
   - Transfer project files
   - Run `build_demo_windows.bat`

## 🚀 Recommendation

**Use GitHub Actions** - it's:
- ✅ FREE
- ✅ FAST (5-10 min per build)
- ✅ NO SETUP (just push code)
- ✅ AUTOMATED (click button, get .exe)

---

**The workflow file is already created for you!**
Just push to GitHub and run it! 🎯

