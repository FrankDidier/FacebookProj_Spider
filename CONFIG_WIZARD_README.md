# ⚙️ Configuration Wizard - User Guide

## 🎯 What's New

A **Configuration Wizard** page has been added to guide users through setup and validate their configuration!

## 📍 Location

The Configuration Wizard is now the **first item** in the sidebar:
- **Sidebar Item**: "⚙️ 配置向导" (Configuration Wizard)
- **Access**: Click the first item in the left sidebar

## ✨ Features

### 1. **Configuration Section**
- **AdsPower Path**: Browse and select AdsPower executable
- **API Key**: Enter AdsPower API key (with show/hide toggle)
- **Account Count**: Set number of accounts to use
- **Save Button**: Save all configuration to `config.ini`

### 2. **System Validation**
Automatically checks:
- ✅ **AdsPower Service**: Is it running?
- ✅ **API Key**: Is it configured?
- ✅ **Facebook Accounts**: Are accounts added to AdsPower?
- ✅ **Data Directories**: Are they created?
- ✅ **Dependencies**: Are packages installed?

### 3. **Visual Status Indicators**
- **Green ✓**: Everything OK
- **Yellow ⚠**: Warning (works but not optimal)
- **Red ✗**: Error (needs fixing)

### 4. **Help Section**
- Step-by-step setup instructions
- Links to AdsPower website
- Tips for best results

## 🚀 How to Use

### Step 1: Open Configuration Wizard
1. Launch the application
2. Click "⚙️ 配置向导" in the sidebar (first item)

### Step 2: Configure Settings
1. **Browse for AdsPower**: Click "浏览..." to find AdsPower executable
2. **Enter API Key**: Get from AdsPower settings, paste here
3. **Set Account Count**: Number of accounts to use simultaneously
4. **Click "保存配置"**: Saves to `config.ini`

### Step 3: Validate
1. Click "🔄 重新验证" button
2. Wait for checks to complete
3. Review status indicators:
   - All green ✓ = Ready to use!
   - Any red ✗ = Fix issues first
   - Yellow ⚠ = Works but could be better

### Step 4: Fix Issues (if any)
- **AdsPower not running**: Start AdsPower Global Browser
- **No API key**: Get from AdsPower → Settings → API
- **No accounts**: Add Facebook accounts in AdsPower
- **Missing directories**: Will be created automatically

## 🔒 Security Features

- **API Key Hidden**: Password field by default
- **Show/Hide Toggle**: Click "显示" to see, "隐藏" to hide
- **Secure Storage**: Saved in `config.ini` (local file)

## ✅ Validation Checks

The wizard checks:

1. **AdsPower Service**
   - Connects to `http://127.0.0.1:50325`
   - Verifies API is responding
   - Shows account count if available

2. **API Key**
   - Checks if key is set in config
   - Validates format (not empty)

3. **Facebook Accounts**
   - Queries AdsPower for accounts
   - Shows count of available accounts
   - Warns if no accounts found

4. **Data Directories**
   - Checks all required folders exist
   - Creates missing directories automatically
   - Verifies write permissions

5. **Dependencies**
   - Checks Python packages installed
   - Lists any missing packages

## 🎨 UI Features

- **Modern Design**: Clean, organized layout
- **Color-Coded Status**: Green/Yellow/Red indicators
- **Progress Bar**: Shows validation in progress
- **Real-Time Updates**: Status updates as checks complete
- **Helpful Messages**: Clear instructions for each issue

## 🔄 Auto-Validation

- **On Page Load**: Automatically runs validation
- **After Save**: Re-validates after saving config
- **Manual**: Click "重新验证" anytime

## 💡 Tips

1. **Run validation first** before using any features
2. **Fix all red errors** before starting
3. **Yellow warnings** are OK but fix for best results
4. **Save config** after making changes
5. **Re-validate** after fixing issues

## 🚨 Error Messages

If validation fails, you'll see:
- **What's wrong**: Clear description
- **How to fix**: Step-by-step instructions
- **Where to go**: Links to relevant settings

## 📋 Integration with Features

All features now check configuration before starting:
- If setup is incomplete, you'll see a warning
- The warning will guide you to the Configuration Wizard
- Features won't start until setup is complete

## 🎉 Benefits

- ✅ **User-Friendly**: No need to edit config.ini manually
- ✅ **Guided Setup**: Step-by-step instructions
- ✅ **Validation**: Know what's wrong before trying features
- ✅ **Visual Feedback**: See status at a glance
- ✅ **Error Prevention**: Catch issues before they cause problems

---

**The Configuration Wizard makes setup easy and ensures everything is ready before using features!** 🚀

