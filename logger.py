from datetime import datetime, timezone

import gspread
import streamlit as st

MAX_CELL_CHARS = 45000  # Google Sheets allows 50,000 characters per cell.


@st.cache_resource
def _worksheet():
    client = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
    return client.open_by_key(st.secrets["SHEET_ID"]).sheet1


def log_session(report, model: str, jd_text: str) -> None:
    # The resume text is never passed to this function, so it cannot be stored.
    row = [
        datetime.now(timezone.utc).isoformat(timespec="seconds"),
        model,
        report.job_title,
        report.match_score,
        ", ".join(report.skills("met")),
        ", ".join(report.skills("partial")),
        ", ".join(report.skills("missing")),
        len(report.roadmap),
        jd_text[:MAX_CELL_CHARS],
        report.model_dump_json()[:MAX_CELL_CHARS],
    ]
    try:
        # RAW stops a cell that starts with "=" from running as a formula.
        _worksheet().append_row(row, value_input_option="RAW")
    except Exception:
        pass  # Logging must never break the user's report.
