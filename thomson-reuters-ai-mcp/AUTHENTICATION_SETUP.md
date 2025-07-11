# Authentication Setup Guide

## Overview

The MCP AI Portal Agent is designed to work with your existing Thomson Reuters login sessions. This guide explains how to properly configure Edge browser to preserve your authentication data.

## 🔐 Key Security Principle

**The agent uses your existing Edge profile to maintain Thomson Reuters authentication**, ensuring you don't need to re-login or provide credentials.

## 🚀 Quick Setup

### Option 1: Use Helper Scripts (Recommended)

1. **Windows Command Prompt**:
   ```cmd
   start-edge-debug.bat
   ```

2. **PowerShell**:
   ```powershell
   .\start-edge-debug.ps1
   ```

### Option 2: Manual Command

```bash
# Windows Command Prompt
"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222

# PowerShell
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222
```

## ⚠️ Critical - What NOT to Do

**DO NOT** use the `--user-data-dir` parameter:
```bash
# ❌ WRONG - This creates a new profile without your login data
msedge.exe --remote-debugging-port=9222 --user-data-dir="C:\temp\edge-debug"
```

**DO** use the default profile:
```bash
# ✅ CORRECT - This preserves your Thomson Reuters login
msedge.exe --remote-debugging-port=9222
```

## 🔍 How It Works

1. **Profile Preservation**: By omitting `--user-data-dir`, Edge uses your default profile
2. **Session Inheritance**: Your existing Thomson Reuters login session is maintained
3. **Seamless Access**: The agent can immediately access the portal without authentication
4. **Security**: No credentials are stored or transmitted by the agent

## 🛠️ Troubleshooting Authentication

### Issue: "Authentication Required" Error

**Solution**: Ensure you're using the default profile:

1. **Close Edge** completely (check Task Manager)
2. **Start Edge with debugging** using the correct command (no `--user-data-dir`)
3. **Verify your login** by navigating to the Thomson Reuters portal manually
4. **Run the agent** - it should now work without authentication issues

### Issue: Edge Won't Start with Debugging

**Solution**: Check for existing Edge processes:

1. **Close all Edge windows**
2. **Check Task Manager** for any remaining `msedge.exe` processes
3. **End any remaining processes**
4. **Try starting Edge with debugging again**

### Issue: Agent Can't Connect to Portal

**Solution**: Verify your Thomson Reuters session:

1. **Open Edge** (with debugging enabled)
2. **Navigate to** `https://dataandanalytics.int.thomsonreuters.com/ai-platform/`
3. **Verify you're logged in** and can access the AI portal
4. **Run the agent** - it should connect successfully

## 🔧 Configuration Notes

### Environment Variables

The agent configuration automatically handles profile preservation:

```env
# Default configuration preserves login data
MCP_BROWSER_DEBUG_PORT=9222
# MCP_BROWSER_USER_DATA_DIR=  # Leave empty for default profile
```

### Profile Detection

The agent automatically:
- Detects your default Edge profile
- Preserves all cookies and session data
- Maintains Thomson Reuters authentication
- Handles session expiration gracefully

## 🎯 Best Practices

1. **Always use the helper scripts** for consistent setup
2. **Keep Edge updated** for security and compatibility
3. **Monitor session expiration** - re-login if needed
4. **Close Edge properly** before starting debugging mode
5. **Test access manually** before running the agent

## 📋 Verification Checklist

Before running the MCP AI Portal Agent:

- [ ] Edge is started with `--remote-debugging-port=9222`
- [ ] No `--user-data-dir` parameter is used
- [ ] You can access http://localhost:9222 in a browser
- [ ] You're logged into Thomson Reuters portal
- [ ] The AI platform is accessible in your browser
- [ ] The agent can connect successfully

## 🆘 Support

If you encounter authentication issues:

1. **Check this guide** for common solutions
2. **Verify your Thomson Reuters access** manually
3. **Test the browser setup** step by step
4. **Review the agent logs** for specific error messages
5. **Contact support** with detailed error information

Remember: The agent is designed to work seamlessly with your existing authentication - no additional login steps should be required!