
import csv
from pathlib import Path

from url_features import extract_url_features


# URLs that were not used for model training
new_urls = [
    "https://www.google.com",
    "https://www.wikipedia.org",
    "https://example.com/login",
    "http://192.168.1.10/verify",
    "https://bit.ly/account-update",
]

output_file = Path("data/new_url_features.csv")

rows = []

for url in new_urls:
    try:
        features = extract_url_features(url)
        features["url"] = url
        rows.append(features)

    except ValueError as error:
        print(f"Skipping {url}: {error}")


# Keep the same 11 feature columns as training
feature_columns = [
    "url_length",
    "uses_https",
    "has_at_symbol",
    "host_is_ip",
    "subdomain_count",
    "has_hyphen_in_hostname",
    "uses_url_shortener",
    "matched_keyword_count",
    "hostname_length",
    "path_length",
    "hostname_digit_count",
]

output_file.parent.mkdir(parents=True, exist_ok=True)

with output_file.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=["url"] + feature_columns
    )
    writer.writeheader()

    for row in rows:
        writer.writerow(row)

print(f"Created: {output_file}")
print(f"URLs processed: {len(rows)}")
