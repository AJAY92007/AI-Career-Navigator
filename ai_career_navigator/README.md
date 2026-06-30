# 🚀 AI Career Navigator

An intelligent resume analyzer and career predictor powered by **Claude AI** and built with **Python + Streamlit**.

---

## ✨ Features

| Feature | Details |
|---|---|
| 📄 PDF Resume Upload | Multi-page PDF extraction using `pypdf` |
| 🎯 Skill Detection | 60+ skills matched with word-boundary accuracy |
| 🚀 Career Prediction | 10 career paths with match % breakdown |
| 📊 Resume Scoring | 100-point score with grade (A+ → D) |
| 🔍 JD Matching | Paste job description or pick skills manually |
| 🤖 AI Advice | Claude AI generates personalized 90-day roadmap |
| 📚 Course Links | Direct links to Coursera, Udemy, YouTube |
| 📥 Report Download | Full .txt report with all analysis |

---

## 🛠 Tech Stack

- **Python 3.10+**
- **Streamlit** — UI framework
- **pypdf** — PDF text extraction
- **Pandas** — Data handling
- **Matplotlib** — Career match chart
- **Claude AI (claude-sonnet-4-6)** — AI suggestions

---

## 🚀 Local Setup

### 1. Clone / extract the project
```bash
cd ai_career_navigator
```

### 2. Create virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`

---

## 🤖 AI Suggestions Setup

To enable the Claude AI-powered career advice:

1. Get a free API key from [console.anthropic.com](https://console.anthropic.com)
2. Enter it in the sidebar → **Anthropic API Key** field
3. OR set it as an environment variable:
   ```bash
   export ANTHROPIC_API_KEY="your-key-here"
   ```

---

## ☁️ Deploy to Streamlit Cloud (Free)

1. Push project to a **GitHub repository**
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub → select `app.py`
4. Add `ANTHROPIC_API_KEY` under **Secrets** in Streamlit Cloud settings:
   ```toml
   ANTHROPIC_API_KEY = "your-key-here"
   ```
5. Click **Deploy** ✅

---

## 📁 Project Structure

```
ai_career_navigator/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## 📊 Resume Score Breakdown

| Check | Points |
|---|---|
| Email Address | 10 |
| Phone Number | 10 |
| GitHub Profile | 10 |
| LinkedIn Profile | 10 |
| Skills (7+ = strong) | 10–20 |
| Projects Section | 15 |
| Certifications | 10 |
| Education | 5 |
| Experience/Internship | 10 |
| **Total** | **100** |

---

## 🏅 Grade Scale

| Score | Grade |
|---|---|
| 90–100 | A+ |
| 80–89 | A |
| 70–79 | B+ |
| 60–69 | B |
| 50–59 | C |
| Below 50 | D |

---
Run the website by click the below link,
https://ai-career-navigator-ajay.streamlit.app

## 👨‍💻 Built By

**Ajay K** — B.Tech AI & Data Science  
Panimalar Engineering College

---

*Current Version: 2.0 | Powered by Claude AI*
