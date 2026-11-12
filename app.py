import time

import streamlit as st
from google.genai import errors

from analyzer import AnalysisError, analyze
from logger import log_session
from parser import CVError, extract_cv_text

MIN_JD_CHARS = 100
MAX_JD_CHARS = 6000
COOLDOWN_SECONDS = 30
MAX_RUNS_PER_SESSION = 5

st.set_page_config(page_title="Career Readiness Report", layout="centered")
st.title("Career Readiness Report")
st.caption("Upload your resume, paste a job description, get a skill-gap roadmap.")

cv_file = st.file_uploader("Resume (text PDF, up to 2 MB)", type=["pdf"])
jd_text = st.text_area("Target job description", height=220, max_chars=MAX_JD_CHARS)
consent = st.checkbox(
    "I understand my resume text is sent to Google's Gemini API on its free tier, "
    "where Google may use it to improve its products. My resume is not stored. This app saves only "
    "the job description and my report for its owner to review."
)
st.caption("Tip: remove your phone number and address from the PDF before uploading.")

st.session_state.setdefault("runs", 0)
st.session_state.setdefault("last_run", 0.0)


def render(report) -> None:
    st.subheader(report.job_title)
    if not report.requirements:
        st.warning(report.summary)
        return

    st.metric("Match score", f"{report.match_score} / 100")
    st.progress(report.match_score / 100)
    st.caption(
        "How the score works: each must-have requirement counts 2 points and each "
        "nice-to-have counts 1. Met earns full points, partial earns half, missing earns none."
    )
    st.write(report.summary)

    st.markdown("**Requirement by requirement**")
    st.table(
        [
            {
                "Requirement": r.skill,
                "Type": r.category,
                "Importance": r.importance,
                "Status": r.status,
                "Evidence in your resume": r.evidence or "-",
            }
            for r in report.requirements
        ]
    )

    if report.roadmap:
        st.markdown("**Learning roadmap**")
        st.table([item.model_dump() for item in report.roadmap])
        st.caption("Course suggestions are AI-generated. Search the platform to confirm they exist.")

    st.download_button("Download report (JSON)", report.model_dump_json(indent=2), "report.json")


if st.button("Analyze Profile", type="primary", disabled=not consent):
    wait = COOLDOWN_SECONDS - (time.time() - st.session_state.last_run)
    if cv_file is None:
        st.warning("Please upload your resume.")
        st.stop()
    if len(jd_text.strip()) < MIN_JD_CHARS:
        st.warning("Please paste the full job description.")
        st.stop()
    if st.session_state.runs >= MAX_RUNS_PER_SESSION:
        st.warning("You have reached the limit for this session.")
        st.stop()
    if wait > 0:
        st.warning(f"Please wait {int(wait) + 1} seconds before the next analysis.")
        st.stop()

    model = st.secrets.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
    try:
        cv_text = extract_cv_text(cv_file.getvalue())
        with st.spinner("Analyzing your profile..."):
            report = analyze(cv_text, jd_text.strip(), st.secrets["GEMINI_API_KEY"], model)
    except (CVError, AnalysisError) as exc:
        st.error(str(exc))
        st.stop()
    except Exception as exc:
        code = getattr(exc, "code", getattr(exc, "status_code", None))
        if code == 429:
            st.error("Today's free AI quota is used up. Please try again tomorrow.")
        else:
            st.error("The AI service is unavailable right now. Please try again shortly.")
        st.stop()

    st.session_state.runs += 1
    st.session_state.last_run = time.time()
    render(report)
    log_session(report, model, jd_text.strip())
