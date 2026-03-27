import streamlit as st
import fitz  # PyMuPDF
import re
from modules.clause_extractor import extract_clauses
from modules.clause_risk import assess_risk
from modules.clause_explainer import explain_clause_plain_english
from modules.clause_rewriter import rewrite_clause
from modules.indian_law_checker import check_indian_law_issues
from modules.ambiguity_detector import detect_ambiguity


# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Clause-by-Clause Contract Analysis",
    page_icon="📑",
    layout="centered"
)

st.title("📑 Clause-by-Clause Contract Analysis")
st.caption("Each clause analysed independently. No legal knowledge needed.")


# -------------------------------------------------
# FILE UPLOAD
# -------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload Contract (PDF or TXT)",
    type=["pdf", "txt"]
)


# -------------------------------------------------
# SAFE FILE READING
# -------------------------------------------------
def read_file(file):
    if file is None:
        return ""

    try:
        if file.name.lower().endswith(".txt"):
            return file.read().decode("utf-8", errors="ignore")

        if file.name.lower().endswith(".pdf"):
            doc = fitz.open(stream=file.read(), filetype="pdf")
            return "\n".join(
                page.get_text()
                for page in doc
                if page.get_text().strip()
            )
    except Exception:
        return ""

    return ""


# -------------------------------------------------
# LIGHTWEIGHT ENTITY EXTRACTION (FACT-BASED)
# -------------------------------------------------
def extract_key_entities(text: str) -> dict:
    t = text.lower()

    entities = {
        "Parties": [],
        "Financial Amounts": [],
        "Timeline / Duration": [],
        "Termination Conditions": [],
        "Confidentiality & NDA": [],
        "Obligations & Liabilities": [],
        "Rights & Ownership": []
    }

    # 👥 PARTIES
    if "lessor" in t and "lessee" in t:
        entities["Parties"].append("Lessor and Lessee")
    elif "landlord" in t and "tenant" in t:
        entities["Parties"].append("Landlord and Tenant")
    elif "employer" in t and "employee" in t:
        entities["Parties"].append("Employer and Employee")

    # 💰 MONEY (ignore tiny / fake values)
    money_matches = re.findall(r"(?:₹|rs\.?)\s?([\d,]{4,})", t)
    for amt in set(money_matches):
        entities["Financial Amounts"].append(f"₹ {amt}")

    # ⏳ DURATION
    for num, unit in re.findall(r"\b(\d{1,2})\s*(months?|years?)\b", t):
        if unit.startswith("year") and int(num) > 30:
            continue
        entities["Timeline / Duration"].append(f"{num} {unit}")

    entities["Timeline / Duration"] = list(set(entities["Timeline / Duration"]))

    # 🛑 TERMINATION
    if any(k in t for k in ["terminate", "termination", "notice period"]):
        entities["Termination Conditions"].append("Termination clause present")

    # 🔒 CONFIDENTIALITY
    if any(k in t for k in ["confidential", "non-disclosure", "nda"]):
        entities["Confidentiality & NDA"].append("Confidentiality obligation present")

    # ⚖️ LIABILITY
    if any(k in t for k in ["liable", "indemnify", "hold harmless"]):
        entities["Obligations & Liabilities"].append("Liability / indemnity obligations present")

    # 📜 OWNERSHIP
    if any(k in t for k in ["intellectual property", "ownership", "shall belong to"]):
        entities["Rights & Ownership"].append("Ownership / IP rights defined")

    return entities


# -------------------------------------------------
# MAIN FLOW
# -------------------------------------------------
if not uploaded_file:
    st.info("⬆️ Upload a contract to begin analysis.")
    st.stop()

text = read_file(uploaded_file)

if not text.strip():
    st.error("❌ Could not extract readable text from this file.")
    st.stop()


with st.spinner("🔍 Extracting clauses..."):
    clauses = extract_clauses(text)

if not clauses:
    st.error("❌ No clauses detected.")
    st.stop()

st.success(f"📑 Total Clauses Detected: {len(clauses)}")


# =================================================
# 🔍 KEY CONTRACT SUMMARY
# =================================================
entities = extract_key_entities(text)

st.markdown("### 🔍 Key Contract Summary")

with st.expander("📌 View Key Contract Details"):
    for title, values in entities.items():
        if values:
            st.markdown(f"**{title}**")
            for v in values:
                st.write(f"• {v}")


st.markdown("---")


# -------------------------------------------------
# CLAUSE-BY-CLAUSE ANALYSIS
# -------------------------------------------------
for i, clause in enumerate(clauses, start=1):

    clause_text = clause.get("text", "").strip()
    clause_type = clause.get("type", "General")

    if len(clause_text) < 30:
        continue

    risk = assess_risk(clause_text)
    risk_level = risk.get("risk_level", "Low")
    reasons = " ".join(risk.get("reasons", []))

    explanation = explain_clause_plain_english(
        clause_text=clause_text,
        clause_type=clause_type,
        forced_risk=risk_level
    )

    law_issues = check_indian_law_issues(clause_text, contract_type=None)

    rewrite = None
    if risk_level in ["Medium", "High"]:
        rewrite = rewrite_clause(
            clause_text,
            risk_level,
            clause_type,
            detect_ambiguity(clause_text),
            law_issues
        )

    with st.expander(
        f"Clause {i} | {clause_type} | Risk: {risk_level}",
        expanded=(risk_level == "High")
    ):
        st.markdown("📄 **Clause Text**")
        st.write(clause_text)

        if risk_level == "High":
            st.error(reasons)
        elif risk_level == "Medium":
            st.warning(reasons)
        else:
            st.success("Low risk clause")

        st.markdown("🧠 **Plain English Explanation**")
        st.write(f"**What it means:** {explanation['what_it_means']}")
        st.write(f"**Why it matters:** {explanation['why_it_matters']}")
        st.write(f"**Favours:** {explanation['favours']}")
        st.info(f"💡 Suggested Action: {explanation['suggested_action']}")

        if law_issues:
            st.warning("🇮🇳 Indian law concerns:")
            for issue in law_issues:
                st.write(f"• {issue}")

        if rewrite:
            st.markdown("✍️ **Safer Rewrite**")
            st.success(rewrite["rewritten_clause"])