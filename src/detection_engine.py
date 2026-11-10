
def detect_suspicious_patterns(features):
    """Analyse URL features and return a risk score with explanations."""

    warnings = []
    risk_score = 0

    # 1. URL contains an @ symbol
    if features.get("has_at_symbol", False):
        risk_score += 20
        warnings.append(
            "URL contains an @ symbol, which can obscure the destination."
        )

    # 2. Hostname is an IP address
    if features.get("host_is_ip", False):
        risk_score += 25
        warnings.append(
            "URL uses an IP address instead of a domain name."
        )

    # 3. URL is unusually long
    if features.get("url_length", 0) > 100:
        risk_score += 10
        warnings.append(
            "URL is longer than 100 characters."
        )

    # 4. URL contains many subdomains
    if features.get("subdomain_count", 0) >= 3:
        risk_score += 15
        warnings.append(
            "Hostname contains three or more estimated subdomain levels."
        )

    # 5. Hostname contains a hyphen
    if features.get("has_hyphen_in_hostname", False):
        risk_score += 5
        warnings.append(
            "Hostname contains a hyphen; inspect the domain carefully."
        )

    # 6. URL uses a known shortening service
    if features.get("uses_url_shortener", False):
        risk_score += 10
        warnings.append(
            "URL uses a known shortening service; inspect its destination."
        )

    # 7. URL contains potentially sensitive keywords
    matched_keywords = features.get("matched_keywords", [])

    if matched_keywords:
        risk_score += min(10 * len(matched_keywords), 20)
        keywords = ", ".join(matched_keywords)
        warnings.append(
            f"URL contains potentially sensitive keywords: {keywords}."
        )

    # Keep the score within the 0–100 range
    risk_score = min(risk_score, 100)

    # Determine the risk level
    if risk_score >= 50:
        risk_level = "High"
    elif risk_score >= 20:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "suspicious": risk_score >= 20,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "warnings": warnings,
        "warning_count": len(warnings),
    }
