# Career Readiness Platform

The **Career Readiness Platform** is a single-page Streamlit web application designed to help job seekers evaluate their fit for target roles. A user uploads a PDF resume and pastes a job description. The app extracts the resume text, compares the candidate's experience against the job requirements using the Google Gemini API with structured outputs, and presents an interactive readiness report.

The entire stack is designed to operate on **100% free-tier** services with zero cloud billing accounts required.

---

## Features

- **Automated Skill-Gap Analysis:** Extracts requirements from the job description, marks them as *must-have* or *nice-to-have*, and evaluates the candidate's qualifications as *met*, *partial*, or *missing* with direct textual evidence from the resume.
- **Deterministic Match Score:** The AI model never computes the score. A fixed Python formula calculates points (must-have = 2 points, nice-to-have = 1 point; met = 1.0, partial = 0.5, missing = 0.0) and computes `round(100 * earned / available)`.
- **Personalized Learning Roadmap:** Suggests focused learning topics, platforms (e.g. Coursera, Udemy), search phrases, and estimated study weeks for all missing or partial skills.
- **Privacy First:** Resume text is never stored or logged anywhere. Only the job description and generated report are logged to Google Sheets for review.
- **Anti-Abuse & Quota Protections:** 2 MB PDF upload limit, 5-page ceiling, text extraction limits (200 min chars, 15,000 max chars), job description size limits (100–6,000 chars), delimiter neutralization to prevent prompt injection, 30-second cooldown between runs, and a 5-run cap per session.

---

## Data Privacy & Storage

- **Resume Text is Ephemeral:** Your uploaded PDF and its extracted text are processed entirely in-memory and sent directly to the Gemini API. The resume text is **never stored, written to disk, or logged** in Google Sheets or server logs.
- **What is Stored:** When connected, the app logs a single row per analysis to a private Google Sheet containing:
  1. `timestamp` (UTC)
  2. `model`
  3. `job_title`
  4. `match_score`
  5. `met_skills`
  6. `partial_skills`
  7. `missing_skills`
  8. `roadmap_items` (count)
  9. `job_description`
  10. `report_json`
- **Free-Tier Model Data Policy:** In accordance with Google's terms for the free Gemini API tier, prompts and responses may be processed to improve products. The app requires an explicit consent confirmation before analysis.

---

## Running Locally

### 1. Prerequisites
- Python 3.11 or newer
- Git

### 2. Setup Virtual Environment
```bash
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt pytest
```

### 4. Configure Secrets
Create `.streamlit/secrets.toml` in the project root:
```toml
GEMINI_API_KEY = "your-gemini-api-key"
GEMINI_MODEL = "gemini-3.5-flash-lite"
SHEET_ID = "your-google-sheet-id"

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "sheet-logger@your-project.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
```
*(Note: Logging stays silent if Google Sheets secrets are not yet configured.)*

### 5. Run the Application
```bash
streamlit run app.py
```
Open your browser to `http://localhost:8501`.

### 6. Run Unit Tests
```bash
pytest -v
```

---

## Deployment to Streamlit Community Cloud

Streamlit Community Cloud hosts public applications at zero cost.

1. **Verify `.gitignore`:** Ensure `.streamlit/secrets.toml` and `.venv/` are listed in `.gitignore` so secrets are never pushed to GitHub:
   ```bash
   git status
   ```
2. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit of Career Readiness Platform"
   git branch -M main
   git remote add origin https://github.com/<YOUR-USERNAME>/<YOUR-REPO-NAME>.git
   git push -u origin main
   ```
3. **Deploy on Streamlit Community Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
   - Click **Create app**.
   - Select your repository, branch (`main`), and set the main file path to `app.py`.
   - Click **Advanced settings**.
   - In the **Secrets** box, paste the entire contents of your local `.streamlit/secrets.toml`.
   - Click **Deploy**.
