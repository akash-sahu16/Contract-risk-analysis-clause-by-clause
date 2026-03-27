import re
from typing import Optional, Dict


def explain_clause_plain_english(
    clause_text: str,
    clause_type: Optional[str] = "General",
    forced_risk: Optional[str] = None
) -> Dict:
    """
    FINAL – Contract-safe clause explanation engine

    ✔ Matches app.py signature (NO crashes)
    ✔ Works for ALL contract types (Lease / Employment / Service / NDA)
    ✔ OCR tolerant
    ✔ Clean favours logic
    ✔ Hackathon-safe (rule based)
    """

    text = (clause_text or "").lower()
    clause_type = (clause_type or "General").lower()

    explanation = {
        "what_it_means": "",
        "why_it_matters": "",
        "risk_level": forced_risk or "Low",
        "favours": "Neutral",
        "suggested_action": "No immediate action required."
    }

    # =================================================
    # 1️⃣ SECURITY DEPOSIT / REFUND (LEASE)
    # =================================================
    if any(k in clause_type for k in ["security", "deposit"]):
        explanation.update({
            "what_it_means":
                "This clause explains how the security deposit will be adjusted or refunded.",
            "why_it_matters":
                "Vague deductions or undefined charges can result in unfair loss of deposit.",
            "favours":
                "Owner / Landlord" if forced_risk in ["Medium", "High"] else "Neutral",
            "suggested_action":
                "Specify exact deductions, timelines, and require proof of expenses."
        })
        return explanation

    # =================================================
    # 2️⃣ PAYMENT / RENT / SALARY
    # =================================================
    if any(k in clause_type for k in ["payment", "financial", "salary", "rent"]):
        explanation.update({
            "what_it_means":
                "This clause explains how and when payments must be made.",
            "why_it_matters":
                "Unclear timelines, penalties, or deductions can create disputes or financial stress.",
            "favours":
                "Owner / Employer" if forced_risk == "High" else "Neutral",
            "suggested_action":
                "Ensure fixed payment dates, clear amounts, and transparent deductions."
        })
        return explanation

    # =================================================
    # 3️⃣ TERMINATION / EVICTION
    # =================================================
    if "termination" in clause_type or "terminate" in text:
        explanation.update({
            "what_it_means":
                "This clause explains when and how the agreement can be terminated.",
            "why_it_matters":
                "Sudden or one-sided termination reduces legal and financial protection.",
            "favours":
                "Owner / Employer" if forced_risk == "High" else "Neutral",
            "suggested_action":
                "Ensure reasonable notice periods and fair termination conditions."
        })
        return explanation

    # =================================================
    # 4️⃣ MAINTENANCE & HANDOVER
    # =================================================
    if any(k in clause_type for k in ["maintenance", "handover", "repair"]):
        explanation.update({
            "what_it_means":
                "This clause sets responsibilities for maintaining and returning the premises.",
            "why_it_matters":
                "Unclear handover standards may lead to disputes, especially over deposits.",
            "suggested_action":
                "Clearly define wear-and-tear versus chargeable damages."
        })
        return explanation

    # =================================================
    # 5️⃣ USE OF PREMISES / RESTRICTIONS
    # =================================================
    if any(k in clause_type for k in ["use", "restriction", "premises"]):
        explanation.update({
            "what_it_means":
                "This clause restricts how the property or service may be used.",
            "why_it_matters":
                "Overly broad restrictions may limit reasonable and lawful usage.",
            "suggested_action":
                "Ensure restrictions are reasonable, lawful, and clearly defined."
        })
        return explanation
    # =================================================
    # 6️⃣ NON-COMPETE / RESTRAINT (INDIA – SECTION 27)
    # =================================================
    if "non-compete" in clause_type or "non compete" in clause_type or "compete" in text:
        explanation.update({
            "what_it_means": (
                "This clause restricts the employee from working in a similar business "
                "after employment ends."
            ),
            "why_it_matters": (
                "Post-employment non-compete clauses are generally unenforceable in India "
                "under Section 27 of the Indian Contract Act."
            ),
            # 🔥 FORCE HIGH RISK (CRITICAL FIX)
            "risk_level": "High",
            "favours": "Employer",
            "suggested_action": (
                "Replace with narrowly scoped confidentiality or non-solicitation clauses "
                "instead of a blanket non-compete."
            )
        })
        return explanation


    # =================================================
    # 7️⃣ PARTY IDENTIFICATION
    # =================================================
    if re.search(r"hereinafter|between\s+mr|tenant|owner|residing at", text):
        explanation.update({
            "what_it_means":
                "This clause identifies the parties to the agreement.",
            "why_it_matters":
                "Incorrect names or addresses can affect legal enforceability.",
            "suggested_action":
                "Verify names, addresses, and identity details carefully."
        })
        return explanation

    # =================================================
    # 8️⃣ ADMINISTRATIVE / EXECUTION DETAILS
    # =================================================
    if re.search(r"stamp|signature|witness|seal|page\s*\d", text):
        explanation.update({
            "what_it_means":
                "This clause records execution or administrative details.",
            "why_it_matters":
                "These confirm document validity but do not create obligations.",
            "suggested_action":
                "Verify stamps, dates, and signatures."
        })
        return explanation

    # =================================================
    # 9️⃣ SAFE FALLBACK (NO FALSE RISK)
    # =================================================
    explanation.update({
        "what_it_means":
            "This clause provides general or supporting terms of the agreement.",
        "why_it_matters":
            "It should not contradict or weaken higher-risk clauses."
    })

        # =================================================
    # 🔟 JURISDICTION / GOVERNING LAW
    # =================================================
    if "jurisdiction" in clause_type or "court" in text or "governing law" in text:
        explanation.update({
            "what_it_means":
                "This clause decides which courts and laws will apply if a dispute arises.",
            "why_it_matters":
                "Unclear or foreign jurisdiction can increase legal cost and complexity.",
            "favours":
                "Owner / Employer" if forced_risk in ["Medium", "High"] else "Neutral",
            "suggested_action":
                "Ensure jurisdiction is clearly defined and convenient to both parties."
        })
        return explanation

    # =================================================
    # 🔟 LIMITATION OF LIABILITY
    # =================================================
    if "limitation" in clause_type or "limit liability" in text:
        explanation.update({
            "what_it_means":
                "This clause limits how much one party can be held financially responsible.",
            "why_it_matters":
                "Unlimited liability can expose a party to excessive financial risk.",
            "favours":
                "Party setting the limit",
            "suggested_action":
                "Ensure liability caps are reasonable and proportionate."
        })
        return explanation

    # =================================================
    # 🔟 INDEMNITY / LIABILITY
    # =================================================
    if "indemnity" in clause_type or "indemnify" in text:
        explanation.update({
            "what_it_means":
                "This clause requires one party to compensate the other for certain losses.",
            "why_it_matters":
                "Broad indemnities can create unpredictable financial exposure.",
            "favours":
                "Benefiting party",
            "suggested_action":
                "Limit indemnity to direct and foreseeable losses."
        })
        return explanation

    # =================================================
    # 🔟 CONFIDENTIALITY / NDA
    # =================================================
    if "confidential" in clause_type or "nda" in text:
        explanation.update({
            "what_it_means":
                "This clause restricts sharing of sensitive or private information.",
            "why_it_matters":
                "Overly long or strict confidentiality may be unenforceable.",
            "favours":
                "Disclosing party",
            "suggested_action":
                "Define scope, duration, and exclusions clearly."
        })
        return explanation

    # =================================================
    # 🔟 INTELLECTUAL PROPERTY
    # =================================================
    if "intellectual" in clause_type or "ip rights" in text:
        explanation.update({
            "what_it_means":
                "This clause defines ownership of ideas, work, or creations.",
            "why_it_matters":
                "Unclear IP ownership can lead to future legal disputes.",
            "favours":
                "Party owning the IP",
            "suggested_action":
                "Clearly specify ownership, usage rights, and transfer terms."
        })
        return explanation
    # =================================================
    # 🔥 OVERRIDE: SECURITY DEPOSIT / DEDUCTION CLAUSE
    # =================================================
    if clause_type == "Damages, Penalties & Deductions":
        return {
            "what_it_means": "The landlord may deduct amounts from the security deposit for rent arrears, utilities, or damages.",
            "why_it_matters": "Without limits, proof, or timelines, deductions can be arbitrary and legally challenged.",
            "risk_level": forced_risk,
            "favours": "Landlord",
            "suggested_action": "Add itemised deductions, reasonable limits, and a clear refund timeline."
        }


    return explanation
