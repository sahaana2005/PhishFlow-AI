
features = extract_url_features(url)
result = detect_suspicious_patterns(features)

predicted_label = 1 if result["suspicious"] else 0

if actual_label == 1 and predicted_label == 0:
    false_negatives.append({
        "url": url,
        "warnings": result["warnings"],
        "risk_score": result.get("risk_score", 0),
    })

elif actual_label == 0 and predicted_label == 1:
    false_positives.append({
        "url": url,
        "warnings": result["warnings"],
        "risk_score": result.get("risk_score", 0),
    })
