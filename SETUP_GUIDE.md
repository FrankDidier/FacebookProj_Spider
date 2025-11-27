# 🚀 Complete Setup Guide - Make Features Work

## ⚠️ Important: Features Require Setup!

The application **requires AdsPower Global Browser** to function. Without it, features will not work.

## 📋 Step-by-Step Setup

### Step 1: Install AdsPower Global Browser

1. **Download AdsPower**
   - Visit: https://www.adspower.com/
   - Download for your OS (Windows/Mac)
   - Install the application

2. **Launch AdsPower**
   - Start AdsPower Global Browser
   - It should run in the background

3. **Get API Key**
   - In AdsPower, go to Settings → API
   - Copy your API key
   - Or generate a new one if needed

### Step 2: Configure Application

1. **Edit `config.ini`**
   ```ini
   [ads]
   key = YOUR_API_KEY_HERE
   service_app_path = C:/Program Files/AdsPower Global/AdsPower Global.exe
   ```
   
   **For macOS:**
   ```ini
   service_app_path = /Applications/AdsPower Global.app/Contents/MacOS/AdsPower Global
   ```

2. **Set Account Numbers**
   ```ini
   [main]
   account_nums = 2  # Number of accounts to use simultaneously
   ```

### Step 3: Add Facebook Accounts to AdsPower

1. **Open AdsPower**
2. **Add Profile**
   - Click "Add Profile" or "Create Profile"
   - Select "Facebook"
   - Enter account credentials
   - Save profile

3. **Login to Facebook**
   - Open the profile in AdsPower
   - Log into Facebook
   - Complete any verification if needed
   - Keep the browser open (or AdsPower will manage it)

4. **Repeat for Multiple Accounts**
   - Add at least 2-3 accounts for better performance
   - More accounts = faster collection

### Step 4: Validate Setup

Run the validation script:

```bash
python3 validate_setup.py
```

**Expected Output:**
```
✅ AdsPower service is running
✅ Facebook accounts configured in AdsPower
✅ All checks passed
```

If you see errors, fix them before proceeding.

### Step 5: Test Features (In Order)

#### Test 1: Collect Groups
1. Open application
2. Go to "采集群组" tab
3. Enter keywords (e.g., "marketing", "business")
4. Click "启动" (Start)
5. Wait for groups to be collected
6. Check `./fb/group/` folder for results

#### Test 2: Collect Members
1. **Prerequisite**: Must have groups collected first
2. Go to "采集成员" tab
3. Click "启动" (Start)
4. Wait for members to be collected
5. Check `./fb/member/` folder for results

#### Test 3: Send Private Messages
1. **Prerequisite**: Must have members collected first
2. Go to "私信成员" tab
3. Enter message text (one per line)
4. Click "启动" (Start)
5. Watch for "私信发送成功" messages

#### Test 4: New Features
- Follow similar pattern
- Check prerequisites
- Enter required input
- Start and monitor

## 🔧 Troubleshooting

### "Cannot connect to AdsPower"
- **Solution**: Make sure AdsPower is running
- Check if service is on port 50325
- Restart AdsPower if needed

### "No accounts found"
- **Solution**: Add Facebook accounts to AdsPower
- Make sure accounts are logged in
- Verify accounts are active (not banned)

### "No groups found"
- **Solution**: Run "采集群组" first
- Enter keywords and collect groups
- Wait for collection to complete

### "No members found"
- **Solution**: Run "采集成员" after collecting groups
- Make sure groups were collected successfully

### Features don't work
- **Check**: Run `validate_setup.py`
- **Check**: Is AdsPower running?
- **Check**: Are accounts configured?
- **Check**: Are prerequisites met?

## ✅ Success Indicators

You'll know it's working when:
- ✅ AdsPower service connects
- ✅ Browser windows open automatically
- ✅ Facebook pages load
- ✅ Data is collected and saved
- ✅ Progress messages appear in UI
- ✅ Files appear in data folders

## 📊 Feature Dependency Chain

```
1. AdsPower Setup
   ↓
2. Collect Groups (采集群组)
   ↓
3. Collect Members (采集成员) - needs groups
   ↓
4. Send Messages (私信成员) - needs members
   ↓
5. New Features - need proper input
```

## 🎯 Quick Checklist

Before testing, ensure:
- [ ] AdsPower is installed
- [ ] AdsPower is running
- [ ] API key is configured in config.ini
- [ ] Path is set in config.ini
- [ ] Facebook accounts added to AdsPower
- [ ] Accounts are logged in
- [ ] Validation script passes
- [ ] Prerequisites are met for each feature

## 💡 Pro Tips

1. **Start with 1-2 accounts** for testing
2. **Use test keywords** first (small groups)
3. **Monitor the UI** for progress messages
4. **Check data folders** for results
5. **Keep AdsPower running** while using the app

---

**Once setup is complete, all features will work!** 🚀

