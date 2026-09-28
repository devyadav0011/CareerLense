# CareerLense

> **“See Your Career Clearly.”**  
> *Secondary Tagline: “Build. Analyze. Improve.”*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Flask%203.0%2B-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Styling](https://img.shields.io/badge/Styling-Tailwind%20CSS-38bdf8.svg)](https://tailwindcss.com/)
[![Tests](https://img.shields.io/badge/Tests-Pytest%2023%2F23%20Passed-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()

---

## 1. Product Overview

**CareerLense** is a modern, AI-powered career and resume platform designed to give job seekers clear, actionable, and truthful visibility into their resumes and job readiness.

Whether starting from a blank page or refining an existing CV, CareerLense empowers users to:
1. **Build** professional resumes from scratch with real-time A4 rendering and multi-template support (Modern, Minimal, Professional).
2. **Upload & Parse** existing PDF and DOCX documents with automated contact, section, and skills taxonomy extraction.
3. **Analyze** resume quality using a deterministic, transparent 7-dimension scoring engine (0–100).
4. **Evaluate ATS Readability** with actionable checkpoints for layout, typography, headings, and data extractability.
5. **Match Against Job Descriptions** to compute job compatibility scores, matched skills, missing skill gaps, and keyword frequency matrices.
6. **Rewrite & Polish** weak bullet points and sections across 6 distinct AI rewrite modes with visual before/after diff highlights.
7. **Export** high-fidelity ATS-friendly PDFs and comprehensive multi-page Analysis Reports.

---

## 2. Core Philosophy: Strictly No Login Required

A core differentiator of CareerLense is complete accessibility:

* **100% Free & Open Access**: Anyone can land on CareerLense, build a resume, upload an existing CV, analyze quality, test ATS readability, match against job descriptions, optimize text with AI, and download production-ready PDFs **without ever creating an account or logging in**.
* **Zero Friction**: No paywalls, no forced email capture, and no sign-up modals blocking your downloads.
* **Ephemeral Session Isolation**: User data and parsed files are managed in private session storage with server-side isolation (`SessionStore`), preventing 4KB cookie limits and ensuring fast performance.
* **Privacy by Design**: A prominent **"Clear All Data"** button allows users to immediately purge all session data and temporary uploaded files with a single click.
* **Optional Cloud Saving**: Authentication (Email/Password) exists solely for users who explicitly choose to save multiple resumes and track historical analysis scores across devices.

---

## 3. Key Capabilities & Feature Set

### 🛠️ Interactive Resume Builder
- Dynamic form sections: Personal Details, Professional Summary, Work Experience, Education, Skills, Projects, and Certifications.
- **AI Polish** buttons embedded directly inside form fields for instant bullet point enhancement.
- Instant, live-rendered A4 preview with real-time typography and spacing updates.
- 3 distinct templates:
  - **Modern**: Accent banners, clean typography, badge pill tags.
  - **Minimal**: Elegant, distraction-free monochrome layout for high-density reading.
  - **Professional**: Classical two-column serif layout favored by traditional industries (Finance, Law, Academia).
- Auto-save to session to prevent accidental data loss.

### 📄 Intelligent Resume Parser
- Supports `.pdf` (dual-engine: PyMuPDF `fitz` + `pypdf` fallback) and `.docx` (`python-docx`).
- Automated contact extraction: Name, Email, Phone, LinkedIn, GitHub, and Portfolio URLs.
- 6-Tier Skills Taxonomy Classifier: Programming Languages, Frameworks, Databases, Cloud & DevOps, Tools, and Methodologies.
- One-click **"Try with a Sample Resume"** button for instant demonstration.

### 📊 Explainable 7-Dimension Scoring Algorithm
CareerLense rejects arbitrary score generators. Every score is fully deterministic, explainable, and calculated from seven weighted categories:
- **Content Quality (20%)**: Action verb frequency, quantifiable metrics, spelling, and buzzword minimization.
- **Skills Coverage (15%)**: Balanced technical and soft skills, organized taxonomy.
- **Project Strength (15%)**: Concrete project descriptions, technologies utilized, and measurable outcomes.
- **Experience Impact (15%)**: Verifiable achievements, chronological progression, and role clarity.
- **Education & Credentials (10%)**: Degree, institution, relevant honors, and certifications.
- **Formatting & Structure (10%)**: Header consistency, bullet point density, and length balance.
- **Completeness (15%)**: Complete contact channels, summary presence, dates, and links.

### 🤖 ATS-Style Readability Index
- Inspects document structure for known parsing hazards: multi-column tables, headers, character encodings, and missing standard section titles.
- Features standard legal/technical disclaimer:  
  *“ATS readability estimates formatting and keyword parsing compatibility. Real ATS systems vary.”*

### 🎯 Job Description Matcher
- Compares resume text and skills directly against any pasted job description.
- Computes overall **Job Match Score (0–100%)**.
- Displays **Matched Skills** (✓) alongside **Missing/Weak Skills** (⚠) with explicit guidance:  
  *“These skills appear in the job description but were not found in your resume. Only add skills you actually possess.”*
- Provides an interactive **Keyword Frequency Matrix** and **5 Job-Specific Recommendations**.

### ✍️ AI Resume Improver & Rewriter
- 6 targeted rewriting styles:
  - **Professional**: Polished, executive tone.
  - **Concise**: Tighter, punchier, removes fluff.
  - **Technical**: Highlights architectures, frameworks, and engineering standards.
  - **Entry-Level**: Emphasizes potential, academic projects, and learning agility.
  - **Impact-Focused**: Leads with measurable results and business outcomes.
  - **ATS-Friendly**: Optimizes for standard terminology and scan readability.
- **Diff Highlighting**: Visual comparison of added text (green) and removed text (strikethrough red).
- Strict AI safety rules: **Never hallucinate fake companies, dates, or numbers**. If metrics are missing, CareerLense prompts: *“Add a measurable result if you have one. Never fabricate numbers.”*

### 📥 PDF Generation Engine
- High-fidelity PDF generation powered by Python `reportlab`.
- Generates clean, print-ready, ATS-compliant resume PDFs across all 3 templates.
- Generates a branded, multi-page **CareerLense Analysis Report PDF** featuring radial score meters, breakdown tables, strengths, weaknesses, and actionable recommendations.

### 💬 CareerLense AI Assistant Drawer
- Globally available slide-out drawer accessible from any page.
- Context-aware resume coaching that answers career queries, reviews bullet points, and suggests interview preparation strategies.

---

## 4. Architecture & Directory Structure

```
CareerLense/
├── app/
│   ├── __init__.py               # Flask application factory & error handlers
│   ├── config.py                 # Configuration settings, scoring weights, limits
│   ├── models/                   # SQLAlchemy models (User, Resume, ResumeAnalysis, JobMatch)
│   │   └── __init__.py
│   ├── routes/                   # Blueprint routes
│   │   ├── __init__.py
│   │   ├── main.py               # Public view pages (Home, Features, How it Works, etc.)
│   │   ├── resume.py             # Resume upload, parsing, and analysis endpoints
│   │   ├── builder.py            # Resume builder save, update, preview endpoints
│   │   ├── job_match.py          # Job description matcher endpoints
│   │   ├── ai.py                 # AI rewriter, summarizer, bullet polish, chat
│   │   ├── export.py             # PDF generation and report export endpoints
│   │   └── auth.py               # Optional account registration, login, cloud storage
│   ├── services/                 # Core domain logic & algorithms
│   │   ├── __init__.py
│   │   ├── parser.py             # PDF/DOCX text & entity extraction
│   │   ├── scorer.py             # 7-dimension deterministic scoring algorithm
│   │   ├── ats_checker.py        # ATS readability inspection
│   │   ├── job_matcher.py        # Resume vs. Job Description matching engine
│   │   ├── ai_service.py         # Multi-provider AI (Gemini, OpenAI, Heuristic fallback)
│   │   └── pdf_service.py        # ReportLab PDF resume & report builder
│   ├── static/                   # Static assets
│   │   ├── css/
│   │   │   └── style.css         # Custom design system, template styles, print rules
│   │   └── js/
│   │       ├── main.js           # Navigation, dark mode, toast alerts, AI drawer
│   │       ├── builder.js        # Split-screen builder form & real-time preview
│   │       ├── analyzer.js       # File drag-and-drop & progress animations
│   │       ├── results.js        # Score dials, radar charts, actionable recommendations
│   │       ├── job_matcher.js    # Job match analysis & gap pill rendering
│   │       └── improver.js       # Before/after diff highlighter & rewriter
│   ├── templates/                # Jinja2 HTML templates
│   │   ├── base.html             # Common layout, nav, AI drawer, footer
│   │   ├── index.html            # Landing page with live preview dashboard
│   │   ├── builder.html          # Interactive resume builder
│   │   ├── analyzer.html         # Resume upload & parsing view
│   │   ├── results.html          # Complete analysis dashboard
│   │   ├── job_matcher.html      # Job matching & skill gap view
│   │   ├── improver.html         # AI rewriter workspace
│   │   ├── preview.html          # Print & download view
│   │   ├── login.html            # Optional sign-in
│   │   ├── register.html         # Optional registration
│   │   ├── saved_resumes.html    # Cloud resume manager
│   │   ├── history.html          # Score tracking history
│   │   ├── features.html         # Detailed platform features
│   │   ├── how_it_works.html     # Workflow explanation
│   │   ├── about.html            # Mission & team
│   │   ├── privacy.html          # Privacy policy & data guarantees
│   │   ├── terms.html            # Terms of service
│   │   └── 404.html              # Custom 404 page
│   └── utils/
│       ├── __init__.py
│       ├── helpers.py            # Formatting & safe file deletion utilities
│       ├── security.py           # Password hashing, filename sanitization, validation
│       └── session_store.py      # Server-side ephemeral session cache
├── instance/                     # Local SQLite DB & server-side session files
├── tests/                        # Comprehensive test suite (23 passing tests)
│   ├── conftest.py               # Pytest fixtures and test client configuration
│   ├── test_parser.py            # PDF/DOCX parsing & text extraction tests
│   ├── test_scorer.py            # Scoring algorithm and weight verification tests
│   ├── test_ats_checker.py       # ATS checks and readability score tests
│   ├── test_job_matcher.py       # Job matching, skill gap, and keyword tests
│   ├── test_ai_service.py        # AI providers, rewrite modes, chat tests
│   ├── test_pdf_service.py       # ReportLab PDF generation tests
│   └── test_routes.py            # End-to-end API and view route tests
├── uploads/                      # Temporary storage for uploaded resumes
├── .env.example                  # Template environment variables
├── .gitignore                    # Git ignore file
├── pytest.ini                    # Pytest configuration
├── requirements.txt              # Production and development dependencies
├── run.py                        # Application entrypoint
└── README.md                     # Comprehensive project documentation
```

---

## 5. Technology Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.10+, Flask 3.0+, Flask-SQLAlchemy, Werkzeug |
| **Document Processing** | PyMuPDF (`pymupdf`), `pypdf`, `python-docx` |
| **PDF Generation** | `reportlab` 4.0+ / 5.0+ |
| **AI Integration** | `google-genai` (Gemini 2.5), `openai` (GPT-4o), Offline Heuristic Engine |
| **Database** | SQLite (zero-config, swappable for PostgreSQL via `DATABASE_URL`) |
| **Frontend** | HTML5, Tailwind CSS, Vanilla JavaScript (ES6+), Chart.js, Lucide Icons |
| **Testing** | `pytest`, `pytest-anyio` |

---

## 6. Installation & Quick Start

### Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/CareerLense.git
cd CareerLense
```

### 2. Create and Activate a Virtual Environment
**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the `.env.example` file to `.env`:
```bash
cp .env.example .env
```
*(On Windows PowerShell: `Copy-Item .env.example .env`)*

Configure your `.env` parameters:
```ini
SECRET_KEY=careerlense-super-secret-key-change-in-production
DATABASE_URL=sqlite:///career_lense.db
AI_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
MAX_UPLOAD_SIZE_MB=10
FLASK_ENV=development
```

> **Note on AI Keys**: If no API key is provided, CareerLense automatically switches to its built-in **Heuristic AI Engine**. You can run, test, and use the entire application offline without an external API key!

### 5. Launch CareerLense
```bash
python run.py
```
Open your browser and navigate to:  
👉 **`http://127.0.0.1:5000`**

---

## 7. Running the Test Suite

CareerLense includes a comprehensive, automated test suite with **23 unit and integration tests** verifying all core services, parsers, algorithms, and routes.

To execute the tests:
```bash
pytest -v
```

### Test Coverage Highlights:
- `test_parser.py`: PDF text extraction (PyMuPDF & pypdf fallback), DOCX parsing, contact regex extraction, 6-category skills taxonomy.
- `test_scorer.py`: 7-dimension weighted scoring math, action verb scanner, metrics detector, suggestion generation.
- `test_ats_checker.py`: Contact extractability, heading standards, table layout warnings, encoding verification.
- `test_job_matcher.py`: Skill gap detection, matched skills check, keyword matrix, recommendation engine.
- `test_ai_service.py`: All 6 rewrite modes, strict anti-hallucination validation, AI chat assistant response format.
- `test_pdf_service.py`: PDF generation for Modern, Minimal, and Professional templates; full analysis report PDF structure.
- `test_routes.py`: Public page views, Builder save & preview, File upload validation, Resume export, Report export, AI helper endpoints, Session clearing, and Optional authentication lifecycle.

---

## 8. Complete Demo & Feature Walkthrough

Follow this step-by-step workflow to explore every feature of CareerLense:

### Step 1: Explore the Homepage (`/`)
- View the hero section highlighting **"No signup required • 100% free to try • Instant analysis"**.
- Interact with the live preview score card demonstrating an 82/100 score, 88% ATS rating, and 78% Job Match.
- Toggle between Light Mode and Dark Mode using the sun/moon icon in the navigation bar.

### Step 2: Build a Resume from Scratch (`/builder`)
- Navigate to **Builder** in the navigation bar.
- Fill in personal details or click **"Load Sample Resume"** to populate realistic engineering data instantly.
- Click **"AI Polish"** next to any job description or summary to see the text instantly enhanced.
- Switch templates between **Modern**, **Minimal**, and **Professional** to see the live A4 preview update in real-time.
- Click **"Download PDF"** to receive your freshly compiled ReportLab PDF.

### Step 3: Analyze an Existing Resume (`/analyzer`)
- Navigate to **Analyzer**.
- Drag and drop a PDF or DOCX resume, or click **"Try with a Sample Resume"** for immediate demonstration without files.
- Watch the 5-step processing sequence (*Extracting text*, *Parsing sections*, *Evaluating ATS*, *AI checks*, *Generating score*).
- You will be automatically redirected to the **Results** page.

### Step 4: Review Score Breakdown & ATS Readability (`/results`)
- Inspect your **Overall Score (0–100)** with color-coded circular dials.
- Review the interactive **Chart.js Radar Chart** displaying individual category scores (Content, Skills, Projects, Experience, Education, Formatting, Completeness).
- Review the **ATS Readability Index** and its checkpoint checklist.
- Review identified **Strengths** and **Weaknesses**.
- Click **"Improve with AI"** next to any recommendation to jump straight to the AI Improver.
- Click **"Download Analysis Report (PDF)"** to generate a complete multi-page audit report.

### Step 5: Test the Job Description Matcher (`/job-matcher`)
- Navigate to **Job Matcher**.
- Your active resume is already loaded in session (or you can paste text directly).
- Paste any job description (or click **"Load Sample Job Description"**).
- Click **"Analyze Match"**.
- View your **Job Match Score**, **Matched Skills (✓)**, **Missing Skills (⚠)**, **Keyword Density Matrix**, and **5 Custom Recommendations**.

### Step 6: Polish Content with the AI Rewriter (`/improver`)
- Navigate to **AI Improver**.
- Select a rewrite style (e.g. *Impact-Focused*, *Concise*, *Technical*, or *ATS-Friendly*).
- Toggle **"Tailor to Job Description"** to include role context.
- Click **"Rewrite with AI"**.
- Inspect the visual diff showing added phrases in green and removed fluff in red.
- Click **"Accept & Apply"** to save changes back to your active resume.

### Step 7: Clear Your Data (`Privacy Guarantee`)
- Click **"Clear All Data"** in the top navigation or footer at any time.
- All session records, cached files, and generated previews are instantly wiped from the server and browser.

---

## 9. API Reference

All core features are available via clean RESTful JSON endpoints:

### Resume & Analyzer API
| Endpoint | Method | Description |
|---|---|---|
| `/api/resume/upload` | `POST` | Upload and analyze a PDF/DOCX file |
| `/api/resume/analyze` | `POST` | Analyze structured resume data and raw text |
| `/api/resume/current` | `GET` | Retrieve the active resume in session |
| `/api/resume/current` | `DELETE` | Delete the current resume from session |
| `/api/resume/clear-session` | `POST` | Wipe all session data and temporary files |

### Builder API
| Endpoint | Method | Description |
|---|---|---|
| `/api/builder/save` | `POST` | Save resume builder form data to session |
| `/api/builder/preview` | `POST` | Render preview data for a specific template |
| `/api/builder/export` | `POST` | Compile and stream resume PDF |

### Job Matcher API
| Endpoint | Method | Description |
|---|---|---|
| `/api/job-match/analyze` | `POST` | Compare resume against a target job description |

### AI Assistant API
| Endpoint | Method | Description |
|---|---|---|
| `/api/ai/analyze` | `POST` | Execute AI quality assessment on resume |
| `/api/ai/improve` | `POST` | Rewrite resume text across 6 modes |
| `/api/ai/summarize` | `POST` | Generate or refine professional summary |
| `/api/ai/project` | `POST` | Optimize project bullet points |
| `/api/ai/chat` | `POST` | Interactive conversational career assistant |

### Export API
| Endpoint | Method | Description |
|---|---|---|
| `/api/export/resume` | `GET`, `POST` | Download resume PDF (Modern, Minimal, Professional) |
| `/api/export/report` | `GET`, `POST` | Download multi-page CareerLense Analysis Report PDF |

### Optional Account API
| Endpoint | Method | Description |
|---|---|---|
| `/api/auth/register` | `POST` | Register optional user account |
| `/api/auth/login` | `POST` | Sign in to access cloud storage |
| `/api/auth/logout` | `POST` | Sign out |
| `/api/auth/me` | `GET` | Get current authenticated user profile |
| `/api/auth/save-resume` | `POST` | Permanently save active resume to user account |
| `/api/auth/saved-resumes` | `GET` | List all saved resumes for the user |
| `/api/auth/saved-resumes/<id>` | `DELETE` | Delete a saved resume from the account |

---

## 10. Privacy & Security Statement

CareerLense adheres to strict privacy and data protection principles:
- **No Mandatory Account**: We never require personal identifying credentials to use the software.
- **Strict File Sanitization**: File names are sanitized with UUID prefixes; uploads are strictly limited to `.pdf` and `.docx` under 10MB.
- **No Data Retention Without Consent**: Uploaded resumes for anonymous users are stored ephemerally and can be purged immediately via the **"Clear All Data"** button.
- **Ethical AI**: We enforce strict prompt-guarding to prevent AI hallucinations. CareerLense never invents fake degrees, certifications, companies, or quantitative numbers.

---

## 11. Contributing & License

Contributions are welcome! Please follow these guidelines:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/AmazingFeature`).
3. Ensure all tests pass (`pytest -v`).
4. Commit your changes (`git commit -m 'Add AmazingFeature'`).
5. Push to the branch (`git push origin feature/AmazingFeature`).
6. Open a Pull Request.

Distributed under the MIT License. See `LICENSE` for more information.

---

**CareerLense** — *“See Your Career Clearly. Build. Analyze. Improve.”*
