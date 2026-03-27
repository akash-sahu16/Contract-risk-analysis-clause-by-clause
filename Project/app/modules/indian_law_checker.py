def check_indian_law_issues(clause_text: str, contract_type=None):
    """
    India-law checker (SAFE)
    Works even if contract_type is None
    """

    if not clause_text:
        return []

    text = clause_text.lower()

    # ✅ SAFE NORMALIZATION
    ct = (contract_type or "").lower()

    issues = []

    # ---------------- NON-COMPETE (INDIA) ----------------
    if "non-compete" in text or "non compete" in text:
        issues.append(
            "Post-employment non-compete clauses are generally void "
            "under Section 27 of the Indian Contract Act."
        )

    # ---------------- SALARY WITHHOLDING ----------------
    if ct == "employment agreement":
        if any(k in text for k in [
            "withhold salary",
            "stop payment",
            "salary may be withheld"
        ]):
            issues.append(
                "Salary withholding may violate the Payment of Wages Act, 1936."
            )

    # ---------------- UNLIMITED LIABILITY ----------------
    if any(k in text for k in [
        "unlimited liability",
        "no maximum limit",
        "fully liable"
    ]):
        issues.append(
            "Unlimited liability without a cap may be legally risky and unenforceable."
        )

    return issues
