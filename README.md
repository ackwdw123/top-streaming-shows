# Top Streaming Shows (Auto‑Updated Daily)

A lightweight, LG‑TV‑friendly dashboard that displays the top trending streaming shows each day.  
This project automatically fetches data, generates a clean HTML page, and publishes it to GitHub Pages for easy viewing on any device — including LG Smart TVs.

---

## 📺 Live Dashboard (LG TV Friendly)

You can access the live, auto‑updated page here:

**https://ackwdw123.github.io/top-streaming-shows/**

This URL can be bookmarked directly on an LG TV using the built‑in web browser.

---

## 🚀 What This Project Does

- Fetches the top trending TV shows from TMDB every day  
- Extracts streaming provider information  
- Generates a TV‑optimized HTML dashboard  
- Publishes the updated page automatically  
- Makes the data available as JSON for other devices or dashboards  

Everything runs without manual intervention.

---

## 🧩 Technical Components

### **1. GitHub Actions (Automation Engine)**
- Runs the update workflow daily (or manually)
- Executes the Python script
- Commits updated files back to the repository
- Publishes the latest version to GitHub Pages

### **2. Python Update Script**
- Fetches trending shows from TMDB API  
- Retrieves streaming provider availability  
- Generates:
  - `index.html` (TV‑friendly dashboard)
  - `data.json` (machine‑readable API output)

### **3. TMDB API**
- Provides trending TV show data  
- Supplies provider availability (Netflix, Hulu, Disney+, etc.)  
- Requires a TMDB API key stored securely as a GitHub Actions secret

### **4. GitHub Pages (Hosting Layer)**
- Serves the dashboard at  
  **https://ackwdw123.github.io/top-streaming-shows/**
- Automatically updates whenever the workflow commits new files

### **5. Icons & Assets**
- Provider icons stored locally in `/icons`
- Used to visually indicate where each show is available to stream

---

## 🛠 Repository Structure
top-streaming-shows/

│ 

├── index.html        # Auto‑generated dashboard 

├── data.json         # Auto‑generated show data 

├── update.py         # Python script that fetches & builds the page 

├── icons/            # Streaming provider icons 

├── .github/ 

    │   
    
    ├── workflows/
    
      ├── update.yml  # GitHub Actions automation 
      
├── README.md


---

## 🔐 Secrets Required

Set the following GitHub Actions secret:

- **TMDB_API_KEY** — your TMDB API key for fetching trending shows and provider data

---

## 🧪 Running Locally (Optional)

If you want to test the script locally:

```bash
pip install requests
export TMDB_API_KEY="your_key_here"
python update.py

This will regenerate index.html and data.json in the repo root.

