# 🚀 Quick Start Guide

## ✅ Status Check (Just Run This!)

```bash
cd /Users/vv/Desktop/src-facebook
source venv/bin/activate
python3 test_run.py
```

If you see "✓ All tests passed!", you're good to go!

---

## 🖥️ How to Run the Application

### Method 1: Simple Run Script
```bash
cd /Users/vv/Desktop/src-facebook
./run.sh
```

### Method 2: Manual Run
```bash
cd /Users/vv/Desktop/src-facebook
source venv/bin/activate
python3 facebook.py
```

---

## 👀 What You Should See

When the application starts successfully:

1. **A GUI Window Opens** with:
   - Title: "Facebook营销" or "Facebook营销 (未注册)"
   - Machine code field (auto-filled with your machine ID)
   - Input fields for:
     - Browser KEY (AdsPower Global API key)
     - Browser EXE address (path to AdsPower executable)
     - Activation code
   - An "激活" (Activate) button

2. **No Errors in Terminal** - The application stays running

3. **Log File Created** - Check `log/src-facebook.log`

---

## 🔍 How to Check if It's Running

### Quick Visual Check
- Look for a window titled "Facebook营销"
- Press `Cmd+Tab` on macOS to see all open applications
- Look for "Python" in the application switcher

### Check Logs
```bash
tail -f log/src-facebook.log
```
You should see INFO messages, not ERROR messages.

### Check Process
```bash
ps aux | grep facebook.py | grep -v grep
```
If you see output, it's running!

---

## ⚙️ First Time Setup

When you first run the application, you'll need to configure:

1. **AdsPower Global Browser KEY**
   - Get this from your AdsPower Global account
   - Paste it in the "浏览器KEY" field

2. **AdsPower Global Browser Path**
   - Click "选择" (Select) button
   - Navigate to: `/Applications/AdsPower Global.app/Contents/MacOS/AdsPower Global`
   - Or wherever you installed AdsPower Global

3. **Activation Code**
   - Enter your license/activation code
   - Click "激活" (Activate) button

---

## 🐛 Troubleshooting

### No Window Appears?

**Check macOS Security:**
1. System Preferences > Security & Privacy
2. Look for Python in the list
3. Click "Allow" if it's blocked

**Run in Terminal to See Errors:**
```bash
cd /Users/vv/Desktop/src-facebook
source venv/bin/activate
python3 facebook.py
```
This will show any error messages.

### Application Crashes?

**Check the log:**
```bash
tail -50 log/src-facebook.log
```

**Reinstall dependencies:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Module not found" Error?

Make sure virtual environment is activated:
```bash
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

---

## 📋 Quick Commands Reference

```bash
# Test if everything works
python3 test_run.py

# Run the application
./run.sh

# Check if running
ps aux | grep facebook.py

# View logs
tail -f log/src-facebook.log

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt
```

---

## ✅ Success Indicators

You'll know it's working when:
- ✓ GUI window opens
- ✓ No error messages in terminal
- ✓ Log file shows INFO messages
- ✓ Application doesn't exit immediately
- ✓ You can see input fields and buttons

---

## 🆘 Still Having Issues?

1. Run the test: `python3 test_run.py`
2. Check logs: `tail -50 log/src-facebook.log`
3. Read full guide: `HOW_TO_CHECK.md`
4. Check README: `README.md`

