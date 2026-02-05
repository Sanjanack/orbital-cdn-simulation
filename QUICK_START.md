# ⚡ Quick Start Guide - Run Your Project in 5 Minutes

## 🚀 Fastest Way to Run

### Step 1: Open Terminal/Command Prompt
```bash
# Navigate to your project folder
cd "D:\VS Code\orbital_cdn_simulation"
```

### Step 2: Activate Virtual Environment
```bash
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### Step 3: Install Dependencies (if not done)
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```

### Step 5: Open Browser
- Go to: **http://localhost:5000**
- Login with: **admin** / **admin123**

**That's it! Your application is running!** ✅

---

## 🎯 For Presentation - Quick Demo Flow

### 1. Login (30 seconds)
- URL: `http://localhost:5000`
- Username: `admin`
- Password: `admin123`

### 2. Request Content (1 minute)
- Go to Content Request tab
- Select any content (e.g., "Daily News Bulletin")
- Click "Request Content"
- Show the delivery process

### 3. Show Analytics (1 minute)
- Go to Analytics tab
- Show charts (Hit Rate, Utilization, Distribution)

### 4. Show Multi-Satellite (1 minute)
- Go to Network View or Satellite Status
- Show constellation view

### 5. Show Admin Dashboard (30 seconds)
- Show user management
- Show system statistics

**Total Demo Time: ~4-5 minutes**

---

## 🆘 Quick Troubleshooting

### Can't start application?
```bash
# Check Python version
python --version

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Port 5000 in use?
```bash
# Change port in app.py (last line)
# From: port=5000
# To: port=5001
# Then access: http://localhost:5001
```

### Database errors?
```bash
# Delete and recreate database
# Windows:
del instance\orbital_cdn.db
python app.py

# Linux/Mac:
rm instance/orbital_cdn.db
python app.py
```

---

## 📞 Need Help?

1. Check `DEMO_AND_PRESENTATION_GUIDE.md` for detailed guide
2. Check `FEATURES_IMPLEMENTATION_SUMMARY.md` for feature details
3. Check `COMPLETE_PROJECT_DOCUMENTATION.md` for full documentation

---

**Good luck with your presentation!** 🎉
