# 🏈 Day 1: Foundation & Data Extraction

## Overview
**Goal**: Set up project infrastructure and validate ESPN API data extraction  
**Time**: 4 hours  
**Deliverable**: Working API client with validated data extraction

---

## ✅ Pre-Flight Checklist

Before starting, ensure you have:
- [ ] Python 3.11+ installed (`python --version`)
- [ ] Git installed
- [ ] VS Code (or your preferred IDE)
- [ ] Terminal/Command Prompt access

---

## 📋 Step-by-Step Instructions

### Step 1: Project Setup (15 minutes)

#### 1.1 Create Project Directory
```bash
# Create and navigate to project folder
mkdir nfl-stats-pipeline
cd nfl-stats-pipeline
```

#### 1.2 Initialize Git Repository
```bash
git init
git add .
git commit -m "Initial project structure"
```

#### 1.3 Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate

# Verify activation (you should see (venv) in your prompt)
```

#### 1.4 Install Dependencies
```bash
# Upgrade pip first
pip install --upgrade pip

# Install all project dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

---

### Step 2: Environment Configuration (15 minutes)

#### 2.1 Create Environment File
```bash
# Copy the example environment file
cp .env.example .env

# Open .env in your editor
code .env  # or: nano .env
```

#### 2.2 Configure .env File
Edit `.env` with these values:

```bash
# Database Configuration (we'll set this up on Day 2)
DATABASE_URL=postgresql://localhost:5432/nfl_stats

# API Configuration
ESPN_API_BASE_URL=http://site.api.espn.com/apis/site/v2/sports/football/nfl

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/etl_pipeline.log

# Pipeline Configuration
CURRENT_SEASON=2024
MAX_RETRIES=3
RETRY_DELAY=5

# Timezone
TIMEZONE=America/New_York
```

#### 2.3 Create Required Directories
```bash
# Create data directories
mkdir -p data/raw
mkdir -p data/processed
mkdir -p logs
mkdir -p dashboards
mkdir -p notebooks
```

---

### Step 3: Test API Client (1.5 hours)

#### 3.1 Test Individual API Client
```bash
# Run the API client test
python -m src.extraction.api_client
```

**Expected Output:**
```
Testing ESPN API Client...
==================================================

1. Fetching current scoreboard...
✓ Found X games
  Sample game: Team A at Team B
  Status: Final

2. Fetching NFL teams...
✓ Found 32 teams
  Sample team: Kansas City Chiefs

3. Determining current week...
✓ Current week: X

4. Fetching standings...
✓ Standings fetched successfully

==================================================
API Client test complete!
Check logs/ directory for detailed logging output.
```

**If errors occur:**
- Check internet connection
- Verify .env file is configured
- Check logs/etl_pipeline.log for details

#### 3.2 Test Helper Utilities
```bash
# Test helper functions
python -m src.utils.helpers
```

#### 3.3 Test Logger
```bash
# Test logging configuration
python -m src.utils.logger
```

---

### Step 4: Comprehensive Data Extraction Test (1 hour)

#### 4.1 Run Day 1 Test Suite
```bash
# Run comprehensive extraction tests
python scripts/day1_test.py
```

**Expected Output:**
```
🏈🏈🏈🏈🏈🏈🏈🏈🏈🏈🏈🏈🏈🏈🏈🏈
NFL STATS ETL PIPELINE - DAY 1 TESTING
🏈🏈🏈🏈🏈🏈🏈🏈🏈🏈🏈🏈🏈🏈🏈🏈

============================================================
TEST 1: Current Scoreboard
============================================================
✓ Season: 2024
✓ Week: X
✓ Games found: Y
✓ Saved to: data/raw/day1_test/scoreboard_weekX.json

Sample Game:
  - Team A at Team B
  - Date: 2024-XX-XX
  - Status: Final
  ...

[Tests continue...]

============================================================
TEST SUMMARY
============================================================
Test 1 - Scoreboard: ✓ PASSED
Test 2 - Teams: ✓ PASSED
Test 3 - Roster: ✓ PASSED
Test 4 - Standings: ✓ PASSED
Test 5 - Historical: ✓ PASSED

------------------------------------------------------------
Total: 5/5 tests passed (100%)
------------------------------------------------------------

✓ Raw data saved to: data/raw/day1_test
✓ Logs saved to: logs/

🏈🏈🏈🏈🏈🏈🏈🏈🏈🏈🏈🏈🏈🏈🏈🏈
DAY 1 COMPLETE!
Next: Day 2 - Database Design & Storage
🏈🏈🏈🏈🏈🏈🏈🏈🏈🏈🏈🏈🏈🏈🏈🏈
```

#### 4.2 Examine Extracted Data
```bash
# View the raw JSON data
ls data/raw/day1_test/

# Open in VS Code to inspect
code data/raw/day1_test/scoreboard_week*.json
```

---

### Step 5: Data Exploration (1 hour)

#### 5.1 Create Jupyter Notebook
```bash
# Start Jupyter
jupyter notebook
```

#### 5.2 Explore Data Structure
Create a new notebook: `notebooks/day1_exploration.ipynb`

```python
import json
import pandas as pd
from pathlib import Path

# Load scoreboard data
with open('data/raw/day1_test/scoreboard_week1.json', 'r') as f:
    scoreboard = json.load(f)

# Explore structure
print("Keys:", scoreboard.keys())
print("Number of games:", len(scoreboard.get('events', [])))

# Extract games into DataFrame
games = []
for event in scoreboard.get('events', []):
    game_data = {
        'game_id': event.get('id'),
        'name': event.get('name'),
        'date': event.get('date'),
        'status': event.get('status', {}).get('type', {}).get('description')
    }
    games.append(game_data)

df_games = pd.DataFrame(games)
print(df_games.head())
```

#### 5.3 Identify Data Points for Metrics

**Document what you found:**
- [ ] Game-level data (ID, date, teams, scores)
- [ ] Team-level data (stats, records)
- [ ] Player-level data (roster, positions)
- [ ] Statistical data (passing, rushing, receiving)

**Take notes on:**
1. Which fields will be used for Clutch Performance Index?
2. Where is snap count data? (for Snap Efficiency)
3. What game situations are available? (4th quarter, close games)

---

## 🎯 Day 1 Deliverables Checklist

By end of Day 1, you should have:

- [x] ✅ Project structure created
- [x] ✅ Virtual environment configured
- [x] ✅ All dependencies installed
- [x] ✅ API client working and tested
- [x] ✅ Sample data extracted and saved
- [x] ✅ Logging system operational
- [x] ✅ Data structure documented

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError"
**Solution:**
```bash
# Make sure virtual environment is activated
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

### Issue: "ESPN API returns empty data"
**Solution:**
- Check if it's NFL off-season (June-August)
- Try different week numbers
- Check logs for specific error messages

### Issue: "Permission denied when creating directories"
**Solution:**
```bash
# Run with appropriate permissions
# Mac/Linux:
sudo mkdir -p logs data
sudo chown -R $USER logs data
```

### Issue: "SSL Certificate Error"
**Solution:**
```bash
# Install certifi
pip install --upgrade certifi

# Or disable SSL verification (not recommended for production)
# Add to api_client.py: verify=False in requests
```

---

## 📊 What You Learned Today

- ✅ How to structure a data engineering project
- ✅ API integration with error handling and retry logic
- ✅ Structured logging for production systems
- ✅ Rate limiting and API best practices
- ✅ Data exploration and validation techniques

---

## 🚀 Next Steps (Day 2 Preview)

Tomorrow you'll:
1. Design normalized database schema
2. Set up PostgreSQL (local + Supabase)
3. Create SQLAlchemy ORM models
4. Implement data loading pipeline
5. Validate data integrity

**Preparation for Day 2:**
- [ ] Create a free Supabase account (https://supabase.com)
- [ ] Install PostgreSQL locally (optional but recommended)
- [ ] Review SQL basics (JOINs, indexes, foreign keys)

---

## 💾 Commit Your Progress

```bash
# Stage all changes
git add .

# Commit Day 1 work
git commit -m "Day 1: API extraction and validation complete"

# Create GitHub repository (if not done yet)
# Follow GitHub's instructions to push your code
```

---

## ⏱️ Time Breakdown

| Task | Estimated | Actual |
|------|-----------|--------|
| Project Setup | 15 min | ___ |
| Environment Config | 15 min | ___ |
| API Client Testing | 1.5 hours | ___ |
| Comprehensive Tests | 1 hour | ___ |
| Data Exploration | 1 hour | ___ |
| **TOTAL** | **4 hours** | ___ |

---

## 📝 Notes & Observations

Use this space to document:
- Any issues encountered
- Interesting data patterns discovered
- Ideas for metrics or visualizations
- Questions for Day 2

```
[Your notes here]
```

---

## ✨ Success Criteria

You've successfully completed Day 1 if:
- ✅ All 5 API tests pass
- ✅ Raw data files created in data/raw/day1_test/
- ✅ Logs directory contains etl_pipeline.log
- ✅ You understand the ESPN API data structure
- ✅ Git repository initialized with first commit

**If all criteria met: YOU'RE READY FOR DAY 2! 🎉**
