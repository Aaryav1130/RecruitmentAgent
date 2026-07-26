# 🤖 RecruitmentAgent – AI Career Assistant for Resume Analysis, Interview Practice & Smart Job Discovery

![Python](https://img.shields.io/badge/Python-3.13+-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.52+-red) ![LangChain](https://img.shields.io/badge/LangChain-Agents-green) ![Groq](https://img.shields.io/badge/Groq-LLaMA3-orange) ![LiveKit](https://img.shields.io/badge/LiveKit-Voice%2FVideo-purple) ![FAISS](https://img.shields.io/badge/RAG-FAISS-blue) ![Multi-Agent](https://img.shields.io/badge/Architecture-MultiAgent-darkgreen)

An end-to-end **AI-driven recruitment automation platform** built with modular agents that handle resume analysis, intelligent job search, and adaptive live interview simulation — all in one seamless pipeline.

RecruitmentAgent automates the full hiring workflow: parse and score resumes against job descriptions using RAG + LLM, search live job listings across multiple platforms, and conduct real-time AI avatar interviews with post-session feedback reports.

---

## 📑 Table of Contents

- [💡 About](#-about)
- [🧩 System Architecture](#-system-architecture)
- [🎬 Demo](#-demo)
- [🛠️ Tech Stack](#%EF%B8%8F-tech-stack)
- [📂 Project Structure](#-project-structure)
- [⚙️ Prerequisites](#%EF%B8%8F-prerequisites)
- [🚀 Installation & Setup](#-installation--setup)
- [🔑 Environment Variables](#-environment-variables)
- [▶️ Running the Application](#%EF%B8%8F-running-the-application)
- [✨ Features Deep Dive](#-features-deep-dive)
- [🤖 Agent Reference](#-agent-reference)
- [📡 API & Backend Reference](#-api--backend-reference)
- [📦 Key Dependencies](#-key-dependencies)
- [📈 Roadmap](#-roadmap)
- [🤝 Contributing](#-contributing)

---

## 💡 About

RecruitmentAgent is a **production-grade multi-agent AI system** that emulates a complete recruitment lifecycle through four autonomous components:

- 📄 **Resume Analysis Agent** — Extracts skills/experience/education, performs JD-vs-resume gap analysis, generates ATS scores, and produces an improved LaTeX resume
- 🔍 **Job Search Agent** — Multi-tier job scraping (JobSpy → SerpAPI → fallback) across LinkedIn, Indeed, Glassdoor, and Naukri
- 🎙️ **Live Interview Agent** — Real-time AI avatar interview via LiveKit + Groq STT/LLM/TTS with Bey avatar integration
- 📊 **Interview Evaluation** — Post-interview LLM-powered scoring, Q&A breakdown, and hire/no-hire recommendation

---

## 🧩 System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Streamlit Frontend (main.py)                     │
│   Tab 1: Resume Analysis  │  Tab 2: Job Search  │  Tab 3: Interview     │
│                           │                     │  Tab 4: Saved Jobs    │
└──────────┬────────────────┴──────────┬──────────┴───────────┬───────────┘
           │                           │                      │
           ▼                           ▼                      ▼
┌─────────────────────┐   ┌─────────────────────┐  ┌──────────────────────────┐
│   Analysis Agent    │   │  Job Search Agent   │  │     Interview Agent      │
│  (analysis_agent.py)│   │(job_search_agent.py)│  │   (interview_agent.py)   │
│                     │   │                     │  │                          │
│ • Docling PDF parse │   │ TIER 1: JobSpy      │  │ • Question generation    │
│ • FAISS RAG store   │   │ TIER 2: SerpAPI     │  │ • LiveKit Room creation  │
│ • Groq LLaMA3 LLM   │   │ TIER 3: Fake safety │  │ • React UI (Vite+JSX)    │
│ • JD match scoring  │   │        net          │  │ • Groq STT + TTS         │
│ • LaTeX resume gen  │   │                     │  │ • Bey AI Avatar          │
└─────────────────────┘   └─────────────────────┘  └──────────────────────────┘
           │                           │                      │
           ▼                           ▼                      ▼
┌─────────────────────┐   ┌─────────────────────┐  ┌──────────────────────────┐
│  HuggingFace        │   │  saved_jobs/        │  │  Flask LiveKit Server    │
│  Embeddings (MiniLM)│   │  (local JSON store) │  │  (livekit_server.py)     │
│  + FAISS VectorStore│   │                     │  │  POST /process-chat      │
└─────────────────────┘   └─────────────────────┘  │  GET  /get-messages      │
                                                   │  GET  /getToken          │
                                                   └──────────────────────────┘
```

---

## 🎬 Demo

### 🖥️ Complete Platform Demo

> A full walkthrough of the RecruitmentAgent platform — resume upload & analysis, job search, interview preparation, and saved jobs.

<video src="https://github.com/user-attachments/assets/e48bc30c-c5f0-412a-bd4d-09948a28d609" controls width="900"></video>


---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Streamlit 1.52+ | Main application UI with multi-tab layout |
| **Interview UI** | React 18 + Vite + LiveKit Components | Real-time video/audio interview interface |
| **LLM** | Groq (LLaMA-3.1-8B-Instant) | Resume analysis, JD matching, interview Q&A |
| **STT** | Groq Whisper Large v3 Turbo | Speech-to-text during live interview |
| **TTS** | Cartesia Sonic-3 (via LiveKit Inference) | AI interviewer voice synthesis |
| **AI Avatar** | Bey (Beyond Presence) | Animated AI interviewer avatar |
| **Voice/Video** | LiveKit Agents + RTC | Real-time communication infrastructure |
| **RAG** | FAISS + HuggingFace `all-MiniLM-L6-v2` | Resume semantic search & QA |
| **PDF Parsing** | Docling + PyPDF2 | High-fidelity resume text extraction |
| **Job Scraping** | JobSpy (python-jobspy) | Real job listings from LinkedIn/Indeed/Glassdoor |
| **Job Search API** | SerpAPI Google Jobs | Fallback job search API |
| **Resume Export** | XeLaTeX (BasicTeX) | Compiled improved PDF resume |
| **Agent Framework** | LangChain + LangChain-Groq | LLM orchestration & chain management |
| **Backend Server** | Flask (async) + Flask-CORS | LiveKit token server & chat relay |
| **Package Manager** | uv | Fast Python dependency management |

---

## 📂 Project Structure

```
RecruitmentAgent/
│
├── agents/                        # Core AI agent modules
│   ├── __init__.py
│   ├── analysis_agent.py          # ResumeAnalysisAgent + Implement wrapper class
│   ├── interview_agent.py         # InterviewAgent — question generation logic
│   └── job_search_agent.py        # JobSearchAgent — 3-tier scraping orchestration
│
├── DEMO/                          # Demo videos
│   ├── demo_video.mp4             # Complete platform walkthrough
│   └── interview_demo.mp4         # Live AI avatar interview demo
│
├── Images/                        # UI assets and logo files
│   ├── 5logo.png
│   ├── cv_template_hero.avif
│   ├── interview.webp
│   └── logo_frontened.png
│
├── Interview/                     # Live interview service (backend + frontend)
│   │
│   ├── agent_runner.py            # LiveKit Agent — STT/LLM/TTS + Bey avatar session
│   ├── livekit_token.py           # LiveKit JWT token generation utility
│   ├── package-lock.json
│   └── prompts.py                 # AGENT_INSTRUCTION + SESSION_INSTRUCTION constants
│   │
│   └── frontend/                  # React + Vite interview UI
│       ├── public/
│       ├── src/
│       │   ├── components/
│       │   │   ├── LiveKitModal.jsx          # LiveKit room connection + PreJoin flow
│       │   │   ├── SimpleVoiceAssistant.jsx  # Interview UI — video, controls, chat
│       │   │   └── SimpleVoiceAssistant.css  # Interview interface styles
│       │   ├── App.css
│       │   ├── App.jsx                       # Root component — hero landing page
│       │   ├── index.css
│       │   └── main.jsx
│       ├── .env.example
│       ├── .gitignore
│       ├── eslint.config.js
│       ├── index.html
│       ├── package-lock.json
│       ├── package.json
│       ├── pnpm-lock.yaml
│       ├── README.md
│       └── vite.config.js
│
├── saved_jobs/                    # Persisted job JSON files per session
│
├── utils/                         # Shared utility modules
│   ├── __init__.py
│   ├── job_scraper.py             # JobScrapper — JobSpy wrapper with date formatting
│   ├── job_storage.py             # save / load / remove saved jobs (local JSON)
│   └── serp_api_searcher.py       # SerpApiSearcher — Google Jobs via SerpAPI
│
├── .env                           # Local environment variables (git-ignored)
├── .env.example                   # Environment variable template
├── .gitignore
├── .python-version                # Pinned Python version (3.13+)
├── config.py                      # API keys, model names, platform config
├── main.py                        # Streamlit entry point — 4-tab UI orchestrator
├── pyproject.toml                 # uv project config — all Python dependencies
├── README.md
├── start.sh                       # Shell script to launch all services
├── ui_utils.py                    # Styling, role_requirements dict, display helpers
└── uv.lock                        # Locked Python dependency versions
```

---

## ⚙️ Prerequisites

Before you begin, ensure you have the following:

✔ **Python 3.13+** (see `.python-version`)  
✔ **Node.js 18+** and **pnpm** (for the React interview frontend)  
✔ **[uv](https://github.com/astral-sh/uv)** — fast Python package manager  
✔ **BasicTeX / TeX Live** — required for LaTeX resume PDF compilation  
✔ **Groq API Key** — [console.groq.com](https://console.groq.com) (free tier available)  
✔ **LiveKit Account** — [cloud.livekit.io](https://cloud.livekit.io) (for live interview)  
✔ **SerpAPI Key** *(optional)* — [serpapi.com](https://serpapi.com) (job search fallback)  
✔ **Bey API Key** *(optional)* — [bey.dev](https://bey.dev) (AI avatar in interview)  

### Installing BasicTeX (macOS — required for Resume PDF export)

```bash
# Install via Homebrew
brew install --cask basictex

# After install, add to PATH and install xelatex
sudo tlmgr update --self
sudo tlmgr install xelatex collection-fontsrecommended
```

> ⚠️ The LaTeX compiler path in `main.py` defaults to:  
> `/usr/local/texlive/2025basic/bin/universal-darwin/xelatex`  
> Update this path in `main.py` → `render_latex_to_pdf()` if your installation differs.

---

## 🚀 Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Rishabh23-Codes/RecruitmentAgent.git
cd RecruitmentAgent
```

### 2️⃣ Install Python Dependencies

```bash
# Install uv if not already installed
pip install uv

# Install all dependencies from pyproject.toml
uv sync
```

### 3️⃣ Install Interview Frontend Dependencies

```bash
cd Interview/frontend
pnpm add @livekit/components-react @livekit/components-styles livekit-client
pnpm install
```

### 4️⃣ Download LiveKit Agent Model Files

```bash
# From the Interview directory
cd Interview
uv run agent_runner.py download-files
```

### 5️⃣ Configure Environment Variables

```bash
cp .env.example .env
```

---

## 🔑 Environment Variables

Edit `.env` with your credentials:

```env
# ─── LLM (Required) ──────────────────────────────────────────────────────────
GROQ_API_KEY=your_groq_api_key_here

# ─── LiveKit (Required for Live Interview) ───────────────────────────────────
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_URL=your_livekit_url
# Example: wss://your-project.livekit.cloud

# ─── Bey AI Avatar (Required for Avatar Interview) ───────────────────────────
BEY_AVATAR_ID=your_bey_avatar_id

# ─── SerpAPI (Optional — Job Search Fallback) ────────────────────────────────
SERPAPI_API_KEY=your_serpapi_key_here
```

> 💡 `GROQ_API_KEY` and `LIVEKIT_*` keys are **required** for core functionality.  
> `SERPAPI_API_KEY` and `BEY_AVATAR_ID` are optional — the app gracefully degrades without them.

---

## ▶️ Running the Application

The platform runs as **four concurrent services**:

### Service 1 — Streamlit App (Main UI)

```bash
uv run streamlit run main.py
```

Accessible at: `http://localhost:8501`

### Service 2 — Flask LiveKit Token Server

```bash
cd Interview
uv run python livekit_token.py
```

Accessible at: `http://localhost:5001`

### Service 3 — LiveKit Interview Agent

```bash
cd Interview
uv run python agent_runner.py dev
```

### Service 4 — React Interview Frontend

```bash
cd Interview/frontend
npm run dev
```

Accessible at: `http://localhost:5173`

### 🔁 Quick Start (All Services)

```bash
./start.sh
```

---

## ✨ Features Deep Dive

### 📄 Tab 1 — Resume Analysis

The resume analysis pipeline runs in two phases for performance:

**Phase 1 — Background Preprocessing** (triggered immediately on upload):
- File text extraction using **Docling** (PDF) or **python-docx** (DOCX)
- Parallel execution via `ThreadPoolExecutor`: builds **FAISS RAG vector store**, extracts contact info (regex), and extracts skills/education/experience via Groq LLaMA3

**Phase 2 — Analysis** (triggered on "Analyze Resume" button):
- JD-vs-Resume comparison using either a **custom uploaded JD** or a **predefined role requirements** list
- Returns: matching skills, missing skills, skill reasoning, ATS score (0–100), job role detection, and overall resume analysis
- Cutoff score for selection: **75/100**

**Sub-tabs within Resume Analysis:**

| Sub-tab | Content |
|---------|---------|
| Summary | ATS score, contact info, job role match, selected/rejected status |
| Skills & Experience | Extracted skills list, education, work experience |
| Analysis | Strengths, improvement areas, content/format/ATS suggestions, detailed weakness breakdown |
| Improved Resume | AI-generated ATS-optimized LaTeX resume compiled to PDF via XeLaTeX |

**Resume Q&A Section** — After analysis, ask any natural language question about your resume using RAG-powered retrieval over resume content.

---

### 🔍 Tab 2 — Job Search

Job search uses a **3-tier fallback architecture** to maximize real job result delivery:

```
TIER 1 → JobSpy (python-jobspy)      Real scraping from LinkedIn/Indeed/Glassdoor/Naukri
    ↓ (if blocked or fails)
TIER 2 → SerpAPI Google Jobs         API-based real job listings with direct apply links
    ↓ (if unavailable)
TIER 3 → Platform-specific fallback  Safe mock listings (demo mode) — clearly flagged
```

**Search Filters Available:**
- Job title (auto-populated from resume analysis result)
- Location (25+ preset cities: India, USA, UK, Germany, Canada)
- Job type: Full-time / Part-time / Contract / Internship
- Experience level slider: 0–1 → 10+ years
- Recency: 1 day → Any time
- Job platforms: LinkedIn, Indeed, Glassdoor, Naukri
- Jobs per platform: 1–10

**Job Detail View:**
- Title, company, location, platform, post date
- Direct apply link (verified real listings marked with ✓)
- Resume match analysis — skill overlap score + recommendations
- Save to local storage or jump directly to Interview Preparation

---

### 🎤 Tab 3 — Interview Preparation

**Mode A — AI-Generated Question Bank** (no job selected):
- Select from 7 interview categories: Technical, Behavioral, Coding, System Design, Project Experience, Cultural Fit, Leadership
- Difficulty levels: Entry Level → Expert
- Category-specific focus area multiselect
- Each question rendered with: question text, context, suggested approach, tips, code solutions (for coding questions), and a personal notes textarea

**Mode B — Job-Specific Preparation** (job selected from Tab 2):
- Questions tailored to the specific job description and your resume
- Same category/difficulty customization as Mode A

**Mode C — Live AI Interview** (checkbox toggle):
- Launches the React interview app at `http://localhost:5173`
- AI avatar (Bey) conducts the interview in real-time
- LiveKit handles STT (Whisper) → LLM (LLaMA3) → TTS (Cartesia Sonic-3) pipeline
- After the interview, click **Generate Report** to:
  1. Fetch conversation transcript from Flask `/get-messages`
  2. Run LLM evaluation on the full conversation
  3. Display: overall score (0–10), per-question scores, strengths, improvements, and hire recommendation

#### 🎥 Live Interview Demo

> Watch the AI avatar interviewer in action — real-time voice, video, transcription, and post-interview evaluation.

<video src="https://github.com/user-attachments/assets/198f8dc9-074b-4d21-93e7-ecc1f015e3ef" controls width="900"></video>


> **Can't play inline?** [📥 Download Interview Demo Video](./DEMO/interview_demo.mp4)

---

### 💼 Tab 4 — Saved Jobs

- All saved jobs persisted to `saved_jobs/` directory as JSON files
- Full job detail view with apply links
- One-click remove from saved list
- Direct "Prepare for Interview" button to transition to Tab 3

---

## 🤖 Agent Reference

### `ResumeAnalysisAgent` (`agents/analysis_agent.py`)

| Method | Description |
|--------|-------------|
| `preprocess_resume(file, job_id)` | Background: extract text, build FAISS store, extract structured info |
| `analyze_system_new(role, custom_jd)` | Full JD-vs-resume comparison, returns scored analysis dict |
| `extract_info_from_resume(text)` | LLM extraction of skills, education, experience as structured JSON |
| `compare_resume_jd_new(...)` | Core RAG + LLM matching — produces matching/missing/extracted skills + ATS score |
| `get_improved_resume(analysis)` | Generates deterministic LaTeX resume from original text |
| `ask_question(question)` | RAG-powered Q&A over resume content |
| `evaluate_interview(conversation)` | LLM evaluation of full interview transcript → structured score report |
| `extract_contact_info(text)` | Regex-based email and phone extraction |

### `JobSearchAgent` (`agents/job_search_agent.py`)

| Method | Description |
|--------|-------------|
| `search_jobs(resume_data, keywords, ...)` | Orchestrates 3-tier search per platform with configurable filters |
| `get_job_match_analysis(resume, job)` | Skill overlap scoring between resume and job description |

### `JobScrapper` (`utils/job_scraper.py`)

| Method | Description |
|--------|-------------|
| `search_jobs(keywords, location, platform, ...)` | JobSpy wrapper with configurable hours window and job type |
| `get_platform_specific_fake_jobs(...)` | Tier 3 emergency fallback with platform-themed mock listings |
| `_format_dataframe(df)` | Normalizes JobSpy DataFrame to standardized job dict format |
| `relative_date(value)` | Converts date/datetime to human-readable "X days ago" |

### `SerpApiSearcher` (`utils/serp_api_searcher.py`)

| Method | Description |
|--------|-------------|
| `search_jobs(keywords, location, platform, count, days_ago)` | Google Jobs API search via SerpAPI with direct apply link extraction |

---

## 📡 API & Backend Reference

### Flask LiveKit Server (`Interview/livekit_server.py`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/getToken` | `GET` | Generates a LiveKit JWT access token. Params: `name`, `room` (optional — auto-generated if omitted) |
| `/process-chat` | `POST` | Accepts an array of chat messages from the React frontend, appends to session store |
| `/get-messages` | `GET` | Returns all accumulated interview chat/transcription messages for evaluation |

**Token generation example:**
```
GET /getToken?name=Rishabh&room=room-abc123
```

### Vite Dev Server Proxy

The React frontend proxies `/api/*` requests to the Flask server on port `5001`. Configure in `vite.config.js`:

```javascript
proxy: {
  '/api': 'http://localhost:5001'
}
```

---

## 📦 Key Dependencies

From `pyproject.toml`:

| Package | Version | Purpose |
|---------|---------|---------|
| `streamlit` | ≥1.52 | Main application UI |
| `langchain-groq` | ≥1.1.1 | Groq LLM integration |
| `langchain-huggingface` | ≥1.2.0 | HuggingFace embeddings |
| `faiss-cpu` | ≥1.13.1 | Vector similarity search |
| `docling` | ≥2.67.0 | Advanced PDF text extraction |
| `python-jobspy` | ≥1.1.82 | Multi-platform job scraping |
| `livekit-agents[bey]` | ~1.3 | LiveKit agent framework + Bey avatar |
| `livekit-plugins-groq` | ≥1.3.6 | Groq STT/LLM within LiveKit |
| `livekit-plugins-silero` | ≥1.3.6 | Voice activity detection |
| `livekit-plugins-turn-detector` | ≥1.3.6 | Multilingual turn detection |
| `flask[async]` | ≥3.1.2 | Async Flask for LiveKit token server |
| `sentence-transformers` | ≥5.2.0 | `all-MiniLM-L6-v2` embeddings |
| `python-docx` | ≥1.2.0 | DOCX resume parsing |

---

## 📈 Roadmap

| Status | Feature |
|--------|---------|
| ✅ | Multi-format resume parsing (PDF, DOCX, TXT) |
| ✅ | RAG-powered resume Q&A |
| ✅ | ATS scoring against custom JD |
| ✅ | LaTeX resume generation & PDF export |
| ✅ | 3-tier job scraping with fallback |
| ✅ | Live AI avatar interview (LiveKit + Bey) |
| ✅ | Post-interview evaluation report |
| 🔜 | LinkedIn OAuth job application tracking |
| 🔜 | Multi-language interview support |
| 🔜 | Interview performance analytics dashboard |
| 🔜 | Persistent user profiles with session history |
| 🔜 | Cover letter generation from resume + JD |
| 🔜 | Docker Compose for one-command multi-service startup |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'feat: add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

Please follow existing code structure — agents go in `agents/`, utilities in `utils/`, and keep UI logic in `ui_utils.py`.

---

## 📄 License

Open source — see the repository for license details.

---

## 👤 Author

**Rishabh**

- 💻 GitHub: [@Rishabh23-Codes](https://github.com/Rishabh23-Codes)
- 🔗 LinkedIn: [Rishabh](https://www.linkedin.com/in/rishabh-503315270/)
- 📧 Email: rishabh23032000@gmail.com

---

> ⭐ If you find **RecruitmentAgent** useful, please give it a star — it helps the project grow!

