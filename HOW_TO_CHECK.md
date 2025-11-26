# How to Check if the Application is Running 🖥️

## Method 1: Check for the GUI Window (Visual Check)

The application should open a **graphical window** with the title "Facebook营销" (Facebook Marketing).

**Look for:**
- A window titled "Facebook营销" or "Facebook营销 (未注册)" 
- The window should have tabs and input fields
- You should see a machine code displayed in the interface

**If you see the window:**
✅ **SUCCESS!** The application is running correctly.

**If you DON'T see a window:**
- Check the terminal/console for error messages
- See Method 2 below to check logs
- The application might need configuration first

---

## Method 2: Check the Log File

The application creates log files in the `log/` directory.

**Check the latest log:**
```bash
cd /Users/vv/Desktop/src-facebook
tail -f log/src-facebook.log
```

**What to look for:**
- ✅ `INFO` messages = Application is working
- ❌ `ERROR` messages = Something went wrong
- ❌ `Traceback` = Python error occurred

**Example of good log:**
```
INFO| machinecode_str=... | mac=... | Serial Number=...
```
This means the application started successfully.

---

## Method 3: Check Running Processes

**Check if Python is running the application:**
```bash
ps aux | grep facebook.py | grep -v grep
```

**Or check all Python processes:**
```bash
ps aux | grep python | grep -v grep
```

**If you see a process:**
✅ The application is running (even if the window isn't visible)

---

## Method 4: Test Import (Quick Check)

**Verify the application can be imported:**
```bash
cd /Users/vv/Desktop/src-facebook
source venv/bin/activate
python3 -c "import facebook; print('✓ Application ready!')"
```

**Expected output:**
```
✓ Application ready!
```

**If you see errors:**
- Check that virtual environment is activated
- Verify all dependencies are installed: `pip list`

---

## Method 5: Check System Activity Monitor (macOS)

1. Open **Activity Monitor** (Applications > Utilities > Activity Monitor)
2. Search for "Python" or "facebook"
3. If you see a Python process running, the application is active

---

## Common Issues & Solutions

### Issue: No GUI Window Appears

**Possible causes:**
1. **macOS Security**: macOS might be blocking the app
   - Go to System Preferences > Security & Privacy
   - Check if Python is blocked
   - Allow it if needed

2. **Display Issues**: The window might be off-screen
   - Try pressing `Cmd+Tab` to switch between applications
   - Look for "Python" in the application switcher

3. **Error on Startup**: Check the terminal/console for errors
   ```bash
   cd /Users/vv/Desktop/src-facebook
   source venv/bin/activate
   python3 facebook.py
   ```
   This will show errors in the terminal

### Issue: Application Crashes Immediately

**Check the log file:**
```bash
tail -50 log/src-facebook.log
```

**Common fixes:**
- Make sure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Check that `config.ini` exists and is valid

### Issue: "Module not found" Errors

**Solution:**
```bash
cd /Users/vv/Desktop/src-facebook
source venv/bin/activate
pip install -r requirements.txt
```

---

## What You Should See When It Works

When the application starts successfully, you should see:

1. **A GUI Window** with:
   - Machine code field (auto-filled)
   - Browser KEY input field
   - Browser EXE address field
   - Activation code input field
   - A "激活" (Activate) button

2. **In the Terminal/Console:**
   - No error messages
   - Application stays running (doesn't exit immediately)

3. **In the Log File:**
   - INFO messages about machine code generation
   - No ERROR or Traceback messages

---

## Quick Status Check Command

Run this one-liner to check everything:
```bash
cd /Users/vv/Desktop/src-facebook && \
echo "=== Process Check ===" && \
ps aux | grep -i "facebook.py\|python.*facebook" | grep -v grep && \
echo -e "\n=== Log Check ===" && \
tail -5 log/src-facebook.log 2>/dev/null || echo "No log file" && \
echo -e "\n=== Import Test ===" && \
source venv/bin/activate && python3 -c "import facebook; print('✓ Ready')" 2>&1 | tail -3
```

---

## Next Steps After Confirming It's Running

1. **Configure the Application:**
   - Enter your AdsPower Global Browser KEY
   - Select the AdsPower Global executable path
   - Enter your activation code
   - Click "激活" (Activate)

2. **Use the Features:**
   - Tab 1: 采集群组 (Collect Groups)
   - Tab 2: 采集成员 (Collect Members)  
   - Tab 3: 私信成员 (Message Members)

---

## Need Help?

If the application isn't working:
1. Check the log file: `log/src-facebook.log`
2. Run it in terminal to see errors: `python3 facebook.py`
3. Verify all dependencies: `pip list`
4. Check the README.md for more troubleshooting

