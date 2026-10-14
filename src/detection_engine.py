
def detect_suspicious_patterns(features):
    """Return warning reasons based on extracted URL features."""

    warnings = []

    if features["has_at_symbol"]:
        warnings.append(
            "URL contains an @ symbol, which can obscure the intended destination."
        )

    if features["host_is_ip"]:
        warnings.append(
            "URL uses an IP address as its host instead of a domain name."
        )

    if features["url_length"] > 100:
        warnings.append(
            "URL is longer than 100 characters and may deserve closer inspection."
        )

    return {
        "suspicious": len(warnings) > 0,
        "warnings": warnings,
    }
