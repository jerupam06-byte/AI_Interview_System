# AI-Powered Interview Preparation & Evaluation System

**Master Placement-Ready Web Application • Flask + PostgreSQL + NLP + OpenAI • Vercel Deployment**  
*Author: Jerusha Pamella Felix M. (MCA Campus Placement Portfolio)*

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-Flask%203.x-green.svg)](https://flask.palletsprojects.com/)
[![NLP Engine](https://img.shields.io/badge/NLP-scikit--learn-orange.svg)](https://scikit-learn.org/)
[![Database](https://img.shields.io/badge/database-PostgreSQL%20%2F%20SQLite-blueviolet.svg)](https://www.postgresql.org/)
[![Deployment](https://img.shields.io/badge/deployment-Vercel-black.svg)](https://vercel.com/)
[![Test Suite](https://img.shields.io/badge/tests-20%20passed%20%28100%25%29-brightgreen.svg)]()

---

## 1. Project Overview

The **AI-Powered Interview Preparation & Evaluation System** is a full-stack web application engineered to prepare MCA/BTech students for campus placements. Candidates select their target job role (**Python Developer**, **AI/ML Engineer**, or **Data Analyst**), choose difficulty and mode, answer technical and behavioral questions by text or voice dictation, and receive instant, explainable NLP-assisted evaluation.

Unlike typical college CRUD applications or black-box LLM wrappers, the core scoring engine operates **deterministically** using TF-IDF vectorization, cosine similarity, boundary-aware multi-word keyword matching, and a transparent weighted scoring system. It introduces a breakthrough differentiating feature: the **Interview Gap Detector**, which extracts demonstrated competencies versus missing concepts and maps them into an actionable revision roadmap.

- **Live Demo Link:** [https://interview-prep-system.vercel.app](https://interview-prep-system.vercel.app) *(Deployable to Vercel via GitHub)*
- **Author:** Jerusha Pamella Felix M.

---

## 2. Key Features

1. **Role-Specific Question Bank:**
   - Pre-seeded curriculum for **Python Developer**, **AI/ML Engineer**, and **Data Analyst**.
   - Spans **Easy**, **Medium**, and **Hard** difficulty levels across **Technical**, **HR / Behavioral**, and **Mixed** categories.
   - Questions are maintained cleanly in JSON and seeded automatically into the database.

2. **Dual Assessment Modes:**
   - **Practice Mode:** Untimed, relaxed learning environment with immediate answer feedback and retry capability.
   - **Real Interview Mode:** Strict 120-second per question timer, hidden benchmark answers, auto-submission on expiration, and holistic end-of-round evaluation.

3. **Speech-to-Text Voice Dictation:**
   - Integrated browser **Web Speech API** for hands-free answer dictation.
   - Real-time pulse indicator while recording.
   - Automatic graceful fallback for browsers without speech recognition; text input is never blocked.

4. **Deterministic Core NLP Evaluation:**
   - **Semantic Similarity (60%):** TF-IDF vectorization and cosine similarity calculation via `scikit-learn`.
   - **Keyword Coverage (20%):** Boundary-aware matching of single and multi-word technical concepts.
   - **Completeness & Structure (10%):** Syntactic boundary analysis and logical reasoning connector detection.
   - **Length / Depth Sanity Check (10%):** Penalizes empty or superficial answers; guarantees empty answers receive 0.

5. **New Differentiating Feature: Interview Gap Detector:**
   - Analyzes candidate answers against benchmark concepts and question topics.
   - Categorizes findings into high-level skills: **Python**, **SQL & Databases**, **Machine Learning**, **NLP**, **Data Analysis & Statistics**, and **HR Communication**.
   - Displays a visual **Skill-Gap Map** dividing concepts into *Demonstrated Knowledge (Strengths)*, *Developing Concepts*, and *Priority Critical Gaps*.
   - Outputs a personalized, prioritized study checklist.

6. **AI Feedback & 24/7 Interview Assistant:**
   - Powered by OpenAI API (`gpt-4o-mini`) for qualitative feedback, strengths/weaknesses synthesis, and model answers.
   - **Zero-Failure Fallback Engine:** If the OpenAI API key is unset or unreachable, an internal deterministic coaching engine provides structured feedback without crashing.

7. **In-Memory Resume Analyzer:**
   - Upload PDF resumes to extract text server-side using `pypdf`.
   - Compares detected technical skills against target role benchmarks and provides match percentages and optimization suggestions.
   - In-memory execution without persisting files on ephemeral disk (safe for serverless runtimes).

8. **Performance Dashboard & Analytics:**
   - Visual charts powered by **Chart.js** displaying score progression over time and a skill-gap radar chart.
   - Algorithmic Placement Readiness Index tracking readiness for Tier-1 interviews.

---

## 3. Technology Stack

| Layer | Technologies Used | Rationale |
| :--- | :--- | :--- |
| **Backend** | Python 3.10+, Flask 3.x, Werkzeug | Lightweight, fast WSGI model, modular blueprints, clear separation of concerns |
| **Database & ORM**| PostgreSQL (Production) / SQLite (Dev), SQLAlchemy | Robust ORM abstraction, ACID transactions, relational integrity, foreign key cascading |
| **NLP & Scoring** | scikit-learn, numpy, scipy | High-performance TF-IDF vectorization, sparse matrix cosine similarity, deterministic metrics |
| **Generative AI** | OpenAI API (`gpt-4o-mini`) with Deterministic Fallback | Generates qualitative feedback and coaching; isolated from numeric scoring |
| **Frontend** | Semantic HTML5, CSS3, Vanilla ES6 JavaScript, Jinja2 | Zero frontend bloat, instant page loads, accessible UI, no complex React build steps |
| **Data Viz** | Chart.js 4.x | Clean canvas rendering for score trends and skill proficiency radar |
| **Voice Dictation**| Browser Web Speech API | Client-side native audio transcription with zero latency and non-blocking fallback |
| **PDF Extraction**| `pypdf` | Fast in-memory parsing of candidate resumes |
| **Deployment** | Vercel (Serverless Python WSGI runtime) | Fast global edge delivery, automatic SSL, seamless GitHub CI/CD integration |

---

## 4. System Architecture

```
                                      +---------------------------------------------+
                                      |             Client Browser (UI)             |
                                      |   HTML5 / Dark AI SaaS CSS / Vanilla JS    |
                                      +----------------------+----------------------+
                                                             |
                                           HTTPS / REST      | Web Speech API (Local STT)
                                                             v
                                      +---------------------------------------------+
                                      |           Vercel WSGI Entrypoint            |
                                      |                  (app.py)                   |
                                      +----------------------+----------------------+
                                                             |
                                      +----------------------v----------------------+
                                      |         Flask Blueprint Routing            |
                                      |  /auth   /interview   /dashboard   /resume  |
                                      +----------------------+----------------------+
                                                             |
               +---------------------------------------------+---------------------------------------------+
               |                                             |                                             |
               v                                             v                                             v
+-------------------------------+             +-------------------------------+             +-------------------------------+
|     Services & NLP Engine     |             |    Persistent Database Layer  |             |      External AI Service      |
|  - services/similarity.py     |             |  - PostgreSQL (Neon / Prod)   |             |  - OpenAI API (gpt-4o-mini)   |
|  - services/keyword_matcher.py| <---------> |  - SQLite (Local Development) |             |  - Deterministic Fallback     |
|  - services/scoring.py        |             |  - models/ (User, Interview,  |             +-------------------------------+
|  - services/gap_detector.py   |             |    Question, Answer, Chat)    |
+-------------------------------+             +-------------------------------+
```

---

## 5. How the Evaluation Algorithm Works

The scoring algorithm calculates a transparent, 4-factor weighted score bounded strictly between 0 and 100:

$$\text{Final Score} = 0.60 \times S_{\text{similarity}} + 0.20 \times S_{\text{keywords}} + 0.10 \times S_{\text{completeness}} + 0.10 \times S_{\text{length}}$$

### A. TF-IDF Cosine Similarity (60%)
Text is pre-processed by lowercasing, stripping punctuation, and filtering English stop-words. `TfidfVectorizer` computes term frequency-inverse document frequency weights across unigrams and bigrams:

$$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \log\left(\frac{1 + |D|}{1 + |\{d \in D : t \in d\}|}\right) + 1$$

Cosine similarity calculates the angle between candidate vector $\vec{u}$ and expected benchmark vector $\vec{v}$:

$$\text{Similarity}(\vec{u}, \vec{v}) = \frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\| \|\vec{v}\|} \times 100$$

### B. Boundary-Aware Multi-Word Keyword Matching (20%)
Technical questions demand precision. Our matcher detects single-word and complex multi-word phrases (e.g. *"global interpreter lock"*, *"star schema"*, *"scaled dot-product"*):

$$S_{\text{keywords}} = \left(\frac{\text{Count of Matched Keywords}}{\text{Total Expected Keywords}}\right) \times 100$$

### C. Completeness & Coherence (10%)
Assesses whether the candidate organized thoughts into structured sentences and used logical connective terminology (*"because"*, *"such as"*, *"for example"*, *"therefore"*, *"in contrast"*).

### D. Length & Relevance Sanity Check (10%)
Verifies answer length relative to expected depth. Short or one-word answers are penalized, and **empty answers receive strictly 0.0**.

---

## 6. Database Schema Design

```
+------------------------------------+
|               users                |
+------------------------------------+
| id (PK, Integer)                   |
| name (String)                      |
| email (String, Unique, Indexed)    |
| password_hash (String)             |
| created_at, updated_at (DateTime)  |
+-----------------+------------------+
                  | 1:N
                  |
+-----------------v------------------+       +------------------------------------+
|             interviews             |       |             questions              |
+------------------------------------+       +------------------------------------+
| id (PK, Integer)                   |       | id (PK, Integer)                   |
| user_id (FK -> users.id)           |       | role, difficulty, category (String)|
| role, difficulty, category (String)|       | topic (String)                     |
| mode (String: 'practice' | 'real') |       | question, expected_answer (Text)   |
| total_questions (Integer)          |       | keywords (JSON string)             |
| final_score (Float)                |       | explanation (Text)                 |
| created_at, completed_at (DateTime)|       | created_at (DateTime)              |
+-----------------+------------------+       +-----------------+------------------+
                  | 1:N                                        | 1:N
                  +---------------------+----------------------+
                                        |
                         +--------------v----------------+
                         |            answers            |
                         +-------------------------------+
                         | id (PK, Integer)              |
                         | interview_id (FK)             |
                         | question_id (FK)              |
                         | answer_text (Text)            |
                         | similarity_score (Float)      |
                         | keyword_score (Float)         |
                         | final_question_score (Float)  |
                         | feedback (JSON Text)          |
                         | created_at (DateTime)         |
                         +-------------------------------+
```

Also includes `chat_history` (assistant conversations) and `resume_analysis` (parsed resume records).

---

## 7. Local Installation & Setup

### Prerequisites
- Python 3.10 or higher
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/jerupam06-byte/AI_Interview_System.git
cd AI_Interview_System
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Update values in `.env`:
```env
SECRET_KEY=your-secure-random-secret-key
# Leave blank for local SQLite or provide your Neon/PostgreSQL connection string:
DATABASE_URL=
# Optional: Set your OpenAI API key for live GPT feedback (deterministic fallback active otherwise)
OPENAI_API_KEY=
FLASK_ENV=development
```

### 5. Run the Application
```bash
python app.py
```
Open your browser at: **`http://localhost:5000`**

---

## 8. Running the Automated Test Suite

The project includes a 20-test automated test suite using `pytest`:

```bash
pytest tests -v
```

**Test Coverage Summary:**
- `test_auth.py`: Registration, email uniqueness, password hashing, protected redirects.
- `test_evaluator.py`: Empty answer guards, TF-IDF cosine similarity, multi-word keywords, 60/20/10/10 weighted formula.
- `test_gap_detector.py`: Keyword taxonomy classification, gap detection, priority categorization.
- `test_resume_analyzer.py`: In-memory PDF text extraction, role skill matching.
- `test_models.py`: User security, question serialization, score calculations.
- `test_routes.py`: Health check, interview setup, question answering, AI chat endpoint.

---

## 9. Vercel Deployment Guide

1. Push your code to GitHub:
   ```bash
   git add .
   git commit -m "feat: complete placement-ready interview preparation system"
   git push origin main
   ```
2. Provision a free PostgreSQL database on [Neon.tech](https://neon.tech).
3. In the Vercel Dashboard, import the repository.
4. Set Environment Variables in **Project Settings → Environment Variables**:
   - `SECRET_KEY`: `random-secure-string`
   - `DATABASE_URL`: `postgres://...` (from Neon)
   - `OPENAI_API_KEY`: `sk-...` (optional)
   - `FLASK_ENV`: `production`
5. Click **Deploy**. Vercel will automatically build the WSGI application using `@vercel/python`.

---

## 10. Placement Interview Explanations (Cheat Sheet)

Questions candidates are frequently asked regarding this project:

- **Why was Flask chosen?**  
  Flask is minimal and gives complete control over request lifecycle, WSGI handlers, and architectural structure without framework overhead.
- **How is user authentication secured?**  
  Passwords are never stored in plaintext; Werkzeug hashes passwords with PBKDF2/SHA-256 and unique per-user salts. Sessions are stored in tamper-proof signed cookies with `HttpOnly` and `SameSite=Lax`.
- **What is the difference between TF-IDF Cosine Similarity and LLM evaluation?**  
  TF-IDF cosine similarity is deterministic, transparent, and mathematically explainable. LLMs can hallucinate numeric grades. Here, the deterministic algorithm computes the score, while LLMs provide qualitative advice.
- **Why use PostgreSQL over SQLite in production?**  
  Vercel serverless functions run in ephemeral, stateless containers where local files are wiped upon cold start. PostgreSQL provides centralized persistence and concurrency.

---

## 11. Author & Acknowledgements

- **Developer:** Jerusha Pamella Felix M.
- **GitHub Profile:** [@jerupam06-byte](https://github.com/jerupam06-byte)
- **Repository:** [AI_Interview_System](https://github.com/jerupam06-byte/AI_Interview_System)
- **Degree:** Master of Computer Applications (MCA)
- **Portfolio Project Focus:** AI Engineering, Full-Stack Python, Placement Preparation
