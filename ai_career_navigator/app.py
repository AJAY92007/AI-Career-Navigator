import streamlit as st
from pypdf import PdfReader
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import re
import json
import requests
import io
from datetime import datetime

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Career Navigator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9ff;
        border: 1px solid #e0e4ff;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .skill-chip {
        display: inline-block;
        background: #e8f5e9;
        color: #2e7d32;
        border-radius: 20px;
        padding: 4px 12px;
        margin: 4px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #4a4a8a;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
        border-left: 4px solid #667eea;
        padding-left: 10px;
    }
    .grade-box {
        font-size: 3rem;
        font-weight: 900;
        text-align: center;
        padding: 1rem;
        border-radius: 12px;
    }
    .stProgress > div > div { border-radius: 10px; }
    div[data-testid="stExpander"] { border: 1px solid #e0e4ff; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
SKILLS_DB = [
    # Languages
    "Python", "SQL", "Java", "C", "C++", "R", "JavaScript", "TypeScript",
    "HTML", "CSS", "Bash", "Scala", "Go", "Rust", "PHP",
    # ML / AI
    "Machine Learning", "Deep Learning", "Artificial Intelligence",
    "Natural Language Processing", "NLP", "Computer Vision",
    "Reinforcement Learning", "Transfer Learning",
    # Frameworks / Libraries
    "TensorFlow", "Keras", "PyTorch", "Scikit-learn", "OpenCV",
    "Pandas", "NumPy", "SciPy", "Matplotlib", "Seaborn",
    "Flask", "Django", "FastAPI", "Streamlit", "React", "Next.js", "Vue",
    "Node.js", "Express", "Spring Boot",
    # Data / BI
    "Power BI", "Tableau", "Excel", "Data Analytics", "Data Visualization",
    "Statistics", "EDA", "Feature Engineering",
    # Cloud / DevOps
    "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes",
    "Git", "GitHub", "GitLab", "CI/CD", "Linux",
    # Databases
    "MongoDB", "MySQL", "PostgreSQL", "Redis", "Elasticsearch",
    "Firebase", "SQLite",
    # Other
    "REST API", "GraphQL", "Microservices", "Agile", "Scrum"
]

CAREER_PATHS = {
    "Data Analyst":      ["Python", "SQL", "Excel", "Power BI", "Tableau", "Data Analytics", "Statistics", "EDA"],
    "Data Scientist":    ["Python", "Machine Learning", "Pandas", "NumPy", "Scikit-learn", "Statistics", "SQL", "Deep Learning"],
    "AI/ML Engineer":    ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Scikit-learn", "NLP", "Computer Vision"],
    "Frontend Developer":["HTML", "CSS", "JavaScript", "TypeScript", "React", "Next.js", "Vue", "Git"],
    "Backend Developer": ["Python", "Java", "Node.js", "Flask", "Django", "FastAPI", "SQL", "MongoDB", "REST API", "Docker"],
    "Full Stack Developer": ["HTML", "CSS", "JavaScript", "React", "Node.js", "SQL", "MongoDB", "Git", "REST API"],
    "DevOps Engineer":   ["Linux", "Docker", "Kubernetes", "AWS", "CI/CD", "Git", "Bash", "Python"],
    "Cloud Engineer":    ["AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Python", "Linux", "CI/CD"],
    "NLP Engineer":      ["Python", "NLP", "Deep Learning", "TensorFlow", "PyTorch", "Machine Learning"],
    "Computer Vision Engineer": ["Python", "Computer Vision", "OpenCV", "Deep Learning", "TensorFlow", "PyTorch"],
}

COURSE_MAP = {
    "Python":           ("Python Bootcamp – Zero to Hero",            "https://www.udemy.com/course/complete-python-bootcamp/"),
    "SQL":              ("SQL for Data Science – Coursera",           "https://www.coursera.org/learn/sql-for-data-science"),
    "Machine Learning": ("ML Specialization – Andrew Ng",            "https://www.coursera.org/specializations/machine-learning-introduction"),
    "Deep Learning":    ("Deep Learning Specialization – deeplearning.ai", "https://www.coursera.org/specializations/deep-learning"),
    "TensorFlow":       ("TensorFlow Developer Certificate",         "https://www.coursera.org/professional-certificates/tensorflow-in-practice"),
    "PyTorch":          ("PyTorch for Deep Learning – freeCodeCamp", "https://www.youtube.com/watch?v=V_xro1bcAuA"),
    "Power BI":         ("Microsoft Power BI Desktop – Udemy",       "https://www.udemy.com/course/microsoft-power-bi-up-running-with-power-bi-desktop/"),
    "Tableau":          ("Tableau Training – Tableau Public",        "https://www.tableau.com/learn/training"),
    "AWS":              ("AWS Certified Cloud Practitioner",         "https://aws.amazon.com/certification/certified-cloud-practitioner/"),
    "Docker":           ("Docker & Kubernetes – Udemy",              "https://www.udemy.com/course/docker-and-kubernetes-the-complete-guide/"),
    "React":            ("React – The Complete Guide – Udemy",       "https://www.udemy.com/course/react-the-complete-guide-incl-redux/"),
    "NLP":              ("NLP with Python – Udemy",                  "https://www.udemy.com/course/nlp-natural-language-processing-with-python/"),
    "Computer Vision":  ("Computer Vision with OpenCV – Udemy",     "https://www.udemy.com/course/python-for-computer-vision-with-opencv-and-deep-learning/"),
    "Scikit-learn":     ("Hands-On ML with Scikit-Learn – O'Reilly","https://www.oreilly.com/library/view/hands-on-machine-learning/9781492032632/"),
    "Git":              ("Git & GitHub – freeCodeCamp",              "https://www.youtube.com/watch?v=RGOj5yH7evk"),
}

# ── Helper Functions ──────────────────────────────────────────────────────────

def extract_text_from_pdf(uploaded_file) -> str:
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def detect_skills(text: str, skills_db: list) -> list:
    detected = []
    for skill in skills_db:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            detected.append(skill)
    return detected

def compute_career_scores(detected_skills: list) -> dict:
    scores = {}
    for role, required in CAREER_PATHS.items():
        matched = [s for s in required if s in detected_skills]
        scores[role] = {
            "score": len(matched),
            "total": len(required),
            "pct": round(len(matched) / len(required) * 100),
            "matched": matched,
            "missing": [s for s in required if s not in detected_skills]
        }
    return scores

def compute_resume_score(text: str, detected_skills: list) -> tuple[int, list]:
    score = 0
    feedback = []
    checks = [
        (r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", 10, "Email Address"),
        (r"(\+91[- ]?)?[6-9]\d{9}",                           10, "Phone Number"),
        (r"github\.com/\S+",                                   10, "GitHub Profile"),
        (r"linkedin\.com/in/\S+",                              10, "LinkedIn Profile"),
    ]
    for pattern, pts, label in checks:
        if re.search(pattern, text, re.IGNORECASE):
            score += pts
            feedback.append(("✅", label, pts))
        else:
            feedback.append(("❌", label, 0))

    if len(detected_skills) >= 7:
        score += 20; feedback.append(("✅", f"Strong Skills Section ({len(detected_skills)} skills)", 20))
    elif len(detected_skills) >= 3:
        score += 10; feedback.append(("⚠️", f"Moderate Skills Section ({len(detected_skills)} skills)", 10))
    else:
        feedback.append(("❌", "Weak Skills Section (fewer than 3 skills)", 0))

    if re.search(r"\bproject", text, re.IGNORECASE):
        score += 15; feedback.append(("✅", "Projects Section", 15))
    else:
        feedback.append(("❌", "Projects Section Missing", 0))

    if re.search(r"\b(certificate|certification|certified)\b", text, re.IGNORECASE):
        score += 10; feedback.append(("✅", "Certifications", 10))
    else:
        feedback.append(("❌", "No Certifications Mentioned", 0))

    if re.search(r"\b(education|b\.tech|bachelor|degree|university|college)\b", text, re.IGNORECASE):
        score += 5; feedback.append(("✅", "Education Section", 5))
    else:
        feedback.append(("❌", "Education Section Missing", 0))

    if re.search(r"\b(internship|intern|experience|worked at)\b", text, re.IGNORECASE):
        score += 10; feedback.append(("✅", "Experience/Internship", 10))
    else:
        feedback.append(("⚠️", "No Internship/Experience Mentioned", 0))

    return min(score, 100), feedback

def get_grade(score: int) -> tuple[str, str]:
    if score >= 90: return "A+", "#2e7d32"
    if score >= 80: return "A",  "#388e3c"
    if score >= 70: return "B+", "#1565c0"
    if score >= 60: return "B",  "#1976d2"
    if score >= 50: return "C",  "#f57c00"
    return "D", "#c62828"

def get_api_key() -> str:
    """Resolve API key: sidebar input > Streamlit secrets > env var."""
    if st.session_state.get("api_key"):
        return st.session_state["api_key"]
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass
    import os
    return os.environ.get("ANTHROPIC_API_KEY", "")

def get_ai_suggestions(resume_text: str, detected_skills: list, best_role: str, missing_skills: list) -> str:
    """Call Claude API for personalized AI suggestions."""
    api_key = get_api_key()
    if not api_key:
        return (
            "⚠️ **No API key found.**\n\n"
            "To enable AI advice, do one of the following:\n"
            "- Enter your key in the sidebar → *Anthropic API Key*\n"
            "- Set `ANTHROPIC_API_KEY` as an environment variable\n"
            "- Add it to `.streamlit/secrets.toml` (for Streamlit Cloud)\n\n"
            "Get a free key at [console.anthropic.com](https://console.anthropic.com)"
        )

    prompt = f"""You are a professional career coach and resume expert.

Analyze this candidate's profile and provide specific, actionable advice.

Detected Skills: {', '.join(detected_skills)}
Best Career Match: {best_role}
Missing Key Skills: {', '.join(missing_skills[:8]) if missing_skills else 'None'}

Resume Text (first 1500 chars):
{resume_text[:1500]}

Provide:
1. 3 specific resume improvement tips (based on what you see)
2. 3 career growth recommendations for {best_role}
3. A 90-day learning roadmap to fill skill gaps
4. One standout project idea to build for their portfolio

Be specific, concise, and encouraging. Format clearly with headers."""

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-sonnet-4-6",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            return data["content"][0]["text"]
        else:
            err = response.json().get("error", {}).get("message", response.text)
            return f"❌ API error {response.status_code}: {err}"
    except Exception as e:
        return f"❌ Could not reach Claude API: {str(e)}"

def render_career_chart(career_scores: dict):
    roles = list(career_scores.keys())
    pcts  = [career_scores[r]["pct"] for r in roles]
    colors = ["#667eea" if p == max(pcts) else "#b0bec5" for p in pcts]

    fig, ax = plt.subplots(figsize=(10, 4))
    bars = ax.barh(roles, pcts, color=colors, edgecolor="white", height=0.6)

    for bar, pct in zip(bars, pcts):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                f"{pct}%", va="center", fontsize=9, fontweight="bold")

    ax.set_xlim(0, 115)
    ax.set_xlabel("Match Percentage (%)", fontsize=10)
    ax.set_title("Career Path Match Analysis", fontsize=12, fontweight="bold", pad=12)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(left=False)
    ax.set_facecolor("#f8f9ff")
    fig.patch.set_facecolor("#ffffff")
    legend = [mpatches.Patch(color="#667eea", label="Best Match"),
              mpatches.Patch(color="#b0bec5", label="Other Roles")]
    ax.legend(handles=legend, loc="lower right", fontsize=8)
    plt.tight_layout()
    return fig

def generate_report(name, best_role, resume_score, grade, detected_skills,
                    feedback, career_scores, ai_suggestions) -> str:
    now = datetime.now().strftime("%d %B %Y, %I:%M %p")
    lines = [
        "=" * 60,
        "       AI CAREER NAVIGATOR – FULL REPORT",
        "=" * 60,
        f"Generated : {now}",
        f"Candidate : {name}",
        "",
        "── RESUME SCORE ────────────────────────────────────────",
        f"  Score : {resume_score}/100",
        f"  Grade : {grade}",
        "",
        "── BEST CAREER MATCH ───────────────────────────────────",
        f"  {best_role}  ({career_scores[best_role]['pct']}% match)",
        "",
        "── DETECTED SKILLS ─────────────────────────────────────",
        "  " + ", ".join(detected_skills) if detected_skills else "  None detected",
        "",
        "── RESUME CHECKLIST ────────────────────────────────────",
    ]
    for icon, label, pts in feedback:
        lines.append(f"  {icon}  {label}" + (f"  (+{pts})" if pts else ""))
    lines += [
        "",
        "── CAREER MATCH BREAKDOWN ──────────────────────────────",
    ]
    for role, data in sorted(career_scores.items(), key=lambda x: -x[1]["pct"]):
        lines.append(f"  {role:<30} {data['pct']:>3}%  ({data['score']}/{data['total']} skills)")
    lines += [
        "",
        "── AI-GENERATED SUGGESTIONS ────────────────────────────",
        ai_suggestions if ai_suggestions else "  (Not generated – upload resume and run analysis)",
        "",
        "=" * 60,
        "  Built with AI Career Navigator | Powered by Ajay K",
        "=" * 60,
    ]
    return "\n".join(lines)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    candidate_name = st.text_input("Your Name (for report)", placeholder="e.g. Ajay K")
    st.markdown("---")
    st.markdown("### 🎯 Target Role Filter")
    target_role = st.selectbox("Focus on role", ["All Roles"] + list(CAREER_PATHS.keys()))
    st.markdown("---")
    st.markdown("### 🤖 AI Suggestions")
    enable_ai = st.toggle("Enable Claude AI Analysis", value=True)
    api_key_input = st.text_input("Anthropic API Key (optional)", type="password",
                                   help="If not set, AI suggestions will be skipped.")
    st.markdown("---")
    st.markdown("### 📌 About")
    st.info("AI Career Navigator analyzes your resume, detects skills, predicts careers, and gives you a personalized roadmap powered by Ajay K.")

# Inject API key into headers via session
if api_key_input:
    st.session_state["api_key"] = api_key_input

# ── Main Header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🚀 AI Career Navigator</h1>
    <p style="font-size:1.1rem; opacity:0.9;">Upload your resume · Detect skills · Predict careers · Get AI-powered advice</p>
</div>
""", unsafe_allow_html=True)

# ── File Upload ───────────────────────────────────────────────────────────────
col_up, col_info = st.columns([2, 1])
with col_up:
    uploaded_file = st.file_uploader("📂 Upload Your Resume (PDF)", type=["pdf"])
with col_info:
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("Supports single-page and multi-page PDF resumes.")

# ── Job Description Input ─────────────────────────────────────────────────────
with st.expander("🎯 Paste Job Description for Matching (optional)"):
    jd_text = st.text_area("Job Description", height=150,
                            placeholder="Paste the job description here to get a match score...")
    jd_skills = detect_skills(jd_text, SKILLS_DB) if jd_text.strip() else []
    if jd_skills:
        st.success(f"Detected {len(jd_skills)} required skills from JD: {', '.join(jd_skills)}")

# ── Analysis ──────────────────────────────────────────────────────────────────
if uploaded_file is not None:
    try:
        with st.spinner("🔍 Analyzing your resume..."):
            text = extract_text_from_pdf(uploaded_file)

        if not text.strip():
            st.error("❌ Could not extract text from PDF. Try a text-selectable PDF.")
            st.stop()

        # Core computations
        detected_skills  = detect_skills(text, SKILLS_DB)
        career_scores    = compute_career_scores(detected_skills)
        resume_score, feedback = compute_resume_score(text, detected_skills)
        grade, grade_color = get_grade(resume_score)

        sorted_careers = sorted(career_scores.items(), key=lambda x: -x[1]["pct"])
        best_role      = sorted_careers[0][0]

        if target_role != "All Roles":
            best_role = target_role

        # ── Top Metrics ───────────────────────────────────────────────────────
        st.markdown("---")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("📊 Resume Score", f"{resume_score}/100")
        m2.metric("🏅 Grade", grade)
        m3.metric("🎯 Skills Found", len(detected_skills))
        m4.metric("🏆 Best Match", best_role)

        st.markdown("---")

        # ── Tabs ──────────────────────────────────────────────────────────────
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🎯 Skills & Career", "📊 Resume Score", "🔍 JD Matching", "🤖 AI Advice", "📄 Resume Text"
        ])

        # ── TAB 1: Skills & Career ────────────────────────────────────────────
        with tab1:
            st.markdown('<div class="section-title">🎯 Detected Skills</div>', unsafe_allow_html=True)
            if detected_skills:
                chips_html = "".join([f'<span class="skill-chip">{s}</span>' for s in detected_skills])
                st.markdown(chips_html, unsafe_allow_html=True)
            else:
                st.warning("No skills detected. Ensure your resume has a clearly labeled Skills section.")

            st.markdown('<div class="section-title">📈 Career Match Chart</div>', unsafe_allow_html=True)
            fig = render_career_chart(career_scores)
            st.pyplot(fig)

            st.markdown('<div class="section-title">🚀 Career Path Details</div>', unsafe_allow_html=True)
            roles_to_show = {k: v for k, v in sorted_careers} if target_role == "All Roles" \
                            else {target_role: career_scores[target_role]}
            for role, data in list(roles_to_show.items())[:6]:
                with st.expander(f"{'🏆 ' if role == best_role else ''}**{role}** — {data['pct']}% match ({data['score']}/{data['total']} skills)"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**✅ You have:**")
                        for s in data["matched"]: st.success(s)
                    with c2:
                        st.markdown("**❌ You need:**")
                        for s in data["missing"]: st.error(s)

        # ── TAB 2: Resume Score ───────────────────────────────────────────────
        with tab2:
            c1, c2 = st.columns([1, 2])
            with c1:
                st.markdown(
                    f'<div class="grade-box" style="background:{grade_color}20;color:{grade_color};border:3px solid {grade_color};">'
                    f'{grade}<br><span style="font-size:1rem;font-weight:400;">Grade</span></div>',
                    unsafe_allow_html=True
                )
                st.markdown("<br>", unsafe_allow_html=True)
                st.progress(resume_score / 100)
                st.markdown(f"<center><b>{resume_score}/100</b></center>", unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="section-title">📋 Checklist</div>', unsafe_allow_html=True)
                for icon, label, pts in feedback:
                    col_a, col_b = st.columns([4, 1])
                    col_a.write(f"{icon} {label}")
                    col_b.write(f"+{pts}" if pts else "—")

            st.markdown('<div class="section-title">💡 Improvement Suggestions</div>', unsafe_allow_html=True)
            suggestions = []
            for icon, label, pts in feedback:
                if icon == "❌":
                    suggestions.append(f"Add your **{label}** to improve your resume score.")
                elif icon == "⚠️":
                    suggestions.append(f"Strengthen your **{label}** section.")
            if len(detected_skills) < 7:
                suggestions.append("Add more technical skills — aim for at least 7-10 relevant ones.")
            if suggestions:
                for s in suggestions: st.warning(s)
            else:
                st.success("🎉 Your resume looks well-structured!")

        # ── TAB 3: JD Matching ────────────────────────────────────────────────
        with tab3:
            st.markdown('<div class="section-title">🔍 Job Description Skill Matcher</div>', unsafe_allow_html=True)
            manual_skills = st.multiselect("Or manually select required skills:", SKILLS_DB)
            target_skills = list(set(jd_skills + manual_skills))

            if target_skills:
                matched  = [s for s in target_skills if s in detected_skills]
                missing  = [s for s in target_skills if s not in detected_skills]
                match_pct = int(len(matched) / len(target_skills) * 100)

                st.metric("Match Score", f"{match_pct}%")
                st.progress(match_pct / 100)

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**✅ Matched Skills**")
                    for s in matched: st.success(s)
                with c2:
                    st.markdown("**❌ Missing Skills**")
                    for s in missing: st.error(s)

                if missing:
                    st.markdown('<div class="section-title">📚 Recommended Courses</div>', unsafe_allow_html=True)
                    for skill in missing:
                        if skill in COURSE_MAP:
                            course_name, url = COURSE_MAP[skill]
                            st.info(f"**{skill}** → [{course_name}]({url})")
                        else:
                            st.info(f"**{skill}** → Search on Coursera / Udemy / YouTube")
            else:
                st.info("Paste a job description above or select skills manually to get a match score.")

        # ── TAB 4: AI Advice ──────────────────────────────────────────────────
        with tab4:
            st.markdown('<div class="section-title">🤖 AI-Powered Personalized Advice</div>', unsafe_allow_html=True)
            if enable_ai:
                if st.button("✨ Generate AI Career Advice", type="primary"):
                    missing_for_role = career_scores[best_role]["missing"]
                    with st.spinner("Claude is analyzing your profile..."):
                        suggestions_text = get_ai_suggestions(text, detected_skills, best_role, missing_for_role)
                    st.session_state["ai_suggestions"] = suggestions_text

                if "ai_suggestions" in st.session_state:
                    st.markdown(st.session_state["ai_suggestions"])
                else:
                    st.info("Click the button above to get AI-generated advice tailored to your resume.")
            else:
                st.info("Enable AI Suggestions from the sidebar to use this feature.")

        # ── TAB 5: Resume Text ────────────────────────────────────────────────
        with tab5:
            st.markdown('<div class="section-title">📄 Extracted Resume Content</div>', unsafe_allow_html=True)
            st.text_area("Full Text", text, height=400)
            st.caption(f"Total characters extracted: {len(text):,}")

        # ── Download Report ───────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### 📥 Download Full Report")
        name_for_report = candidate_name if candidate_name else "Candidate"
        ai_sugg = st.session_state.get("ai_suggestions", "(Generate AI Advice in Tab 4 to include here)")
        report_text = generate_report(
            name_for_report, best_role, resume_score, grade,
            detected_skills, feedback, career_scores, ai_sugg
        )
        st.download_button(
            label="📥 Download Report (.txt)",
            data=report_text,
            file_name=f"career_report_{name_for_report.replace(' ', '_')}.txt",
            mime="text/plain",
            type="primary"
        )

    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.exception(e)
else:
    # ── Landing ───────────────────────────────────────────────────────────────
    st.markdown("### 👇 How It Works")
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown("**1️⃣ Upload PDF**\nDrop your resume PDF above")
    c2.markdown("**2️⃣ Skill Detection**\n40+ skills auto-detected")
    c3.markdown("**3️⃣ Career Matching**\n10 career paths analysed")
    c4.markdown("**4️⃣ AI Advice**\nPersonalized Claude AI tips")
    st.markdown("---")
    st.info("📂 Upload your resume PDF to begin. Supported: single & multi-page resumes.")
