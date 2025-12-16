# Windows Task Scheduler Setup (Manual Steps)

## You need to do this ONCE manually (takes 5 minutes):

### Step 1: Open Task Scheduler as Administrator
1. Press `Win + X`
2. Click "Task Scheduler" (or search for it)
3. If prompted, allow admin access

---

### Step 2: Create Shorts Task

1. Click "Create Basic Task..." in right panel
2. **Name**: `YouTube-Shorts-Hourly`
3. **Description**: `Generates YouTube Shorts every hour`
4. Click "Next"

5. **Trigger**: Select "Daily"
6. Click "Next"
7. **Start**: Today's date, **Time**: Current time
8. Click "Next"

9. **Action**: "Start a program"
10. Click "Next"

11. **Program/script**: Browse to:
   ```
   C:\Users\shivg\OneDrive\Desktop\yt workflow\run_shorts.bat
   ```
12. Click "Next"
13. Check "Open Properties dialog when I click Finish"
14. Click "Finish"

---

### Step 3: Configure Advanced Settings for Shorts Task

In the Properties window that opens:

1. **General tab**:
   - ✅ Check "Run whether user is logged on or not" (optional)
   - ✅ Check "Run with highest privileges"

2. **Triggers tab**:
   - Click "Edit"
   - ✅ Check "Repeat task every: **1 hour**"
   - ✅ For a duration of: **Indefinitely**
   - Click "OK"

3. **Settings tab**:
   - ✅ Check "Allow task to be run on demand"
   - ✅ Check "Run task as soon as possible after scheduled start is missed"
   - ✅ Check "If the task fails, restart every: **10 minutes**"
   - Uncheck "Stop the task if it runs longer than"
   - OR set to "2 hours" if you want a safety limit

4. Click "OK"

---

### Step 4: Create Long Videos Task

Repeat Step 2 & 3 with these changes:

- **Name**: `YouTube-Long-Hourly`
- **Description**: `Generates long-form videos every hour`
- **Program/script**: Browse to:
  ```
  C:\Users\shivg\OneDrive\Desktop\yt workflow\run_long.bat
  ```
- **Trigger**: Repeat every **1 hour**, but offset by **30 minutes**
  - If Shorts runs at :00, set Long to start at :30
  - Example: If it's 3:15 PM now, set Long to start at 3:30 PM

---

### Step 5: Test Both Tasks

1. In Task Scheduler, find "YouTube-Shorts-Hourly"
2. Right-click → "Run"
3. Watch it generate a video
4. Repeat for "YouTube-Long-Hourly"

---

### Step 6: Monitor Tasks

**View task history:**
1. Task Scheduler Library
2. Click your task
3. Click "History" tab (bottom)

**View logs:**
- Check Task Scheduler history for execution times
- Your Python scripts will show output in real-time when running

---

## ✅ Done!

Your automation now runs:
- **Shorts**: Every hour at :00 (e.g., 1:00, 2:00, 3:00...)
- **Long videos**: Every hour at :30 (e.g., 1:30, 2:30, 3:30...)
- **Only when**: Your PC is turned on
- **Cost**: $0
- **Maintenance**: None

---

## Troubleshooting:

### Task doesn't run:
1. Check if PC was on at scheduled time
2. Right-click task → Run (to test manually)
3. Check "Last Run Result" column
4. View History tab for errors

### Script fails:
- Open PowerShell and run manually:
  ```powershell
  cd "C:\Users\shivg\OneDrive\Desktop\yt workflow"
  .\run_shorts.bat
  ```
- Check for Python errors

### Want to disable:
- Right-click task → Disable

### Want to change schedule:
- Right-click task → Properties → Triggers → Edit

---

## Optional: Create Desktop Shortcuts

### Quick Run Shorts:
1. Right-click Desktop → New → Shortcut
2. Location: `C:\Users\shivg\OneDrive\Desktop\yt workflow\run_shorts.bat`
3. Name: "Generate YouTube Short"

### Quick Run Long:
1. Right-click Desktop → New → Shortcut
2. Location: `C:\Users\shivg\OneDrive\Desktop\yt workflow\run_long.bat`
3. Name: "Generate Long Video"

Now you can manually trigger videos anytime by double-clicking!

---

## That's it! 🎉

Your YouTube automation is now running locally, free forever, whenever your PC is on.
