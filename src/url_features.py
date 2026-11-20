
from urllib.parse import urlsplit
import ipaddress


def extract_url_features(url):
    """Validate an HTTP(S) URL and extract 11 numerical features."""

    if not isinstance(url, str):
        raise ValueError("URL must be provided as text.")

    url = url.strip()

    if not url:
        raise ValueError("URL cannot be empty.")

    try:
        parsed = urlsplit(url)
    except ValueError as error:
        raise ValueError("Malformed URL.") from error

    if parsed.scheme.lower() not in ("http", "https"):
        raise ValueError("Only HTTP and HTTPS URLs are supported.")

    try:
        hostname = parsed.hostname
        parsed.port
    except ValueError as error:
        raise ValueError("Invalid hostname or port.") from error

    if not hostname:
        raise ValueError("URL must contain a hostname.")

    hostname = hostname.lower().rstrip(".")

    # 1. Basic URL features
    url_length = len(url)
    uses_https = int(parsed.scheme.lower() == "https")
    has_at_symbol = int("@" in url)

    # 2. IP address detection
    try:
        ipaddress.ip_address(hostname)
        host_is_ip = 1
    except ValueError:
        host_is_ip = 0

    # 3. Estimated subdomain count
    if host_is_ip:
        subdomain_count = 0
    else:
        hostname_labels = hostname.split(".")
        subdomain_count = max(0, len(hostname_labels) - 2)

    # 4. Hyphen detection
    has_hyphen_in_hostname = int("-" in hostname)

    # 5. URL shortener detection
    shortener_domains = {
        "bit.ly",
        "is.gd",
        "t.co",
        "tinyurl.com",
        "ow.ly",
        "buff.ly",
        "cutt.ly",
        "rebrand.ly",
    }

    uses_url_shortener = int(hostname in shortener_domains)

    # 6. Suspicious keyword count
    suspicious_keywords = (
        "login",
        "verify",
        "account",
        "password",
    )

    url_lower = url.lower()

    matched_keyword_count = sum(
        keyword in url_lower
        for keyword in suspicious_keywords
    )

    # 7. Additional hostname and path features
    hostname_length = len(hostname)
    path_length = len(parsed.path)

    hostname_digit_count = sum(
        character.isdigit() for character in hostname
    )

    return {
        "url_length": url_length,
        "uses_https": uses_https,
        "has_at_symbol": has_at_symbol,
        "host_is_ip": host_is_ip,
        "subdomain_count": subdomain_count,
        "has_hyphen_in_hostname": has_hyphen_in_hostname,
        "uses_url_shortener": uses_url_shortener,
        "matched_keyword_count": matched_keyword_count,
        "hostname_length": hostname_length,
        "path_length": path_length,
        "hostname_digit_count": hostname_digit_count,
    }


if __name__ == "__main__":

    sample_url = "https://bit.ly/login/example"

    try:
        features = extract_url_features(sample_url)

        print("URL:", sample_url)
        print("\nExtracted features:")

        for feature, value in features.items():
            print(f"{feature}: {value}")

        print("\nTotal features:", len(features))

    except ValueError as error:
        print("Input error:", error)
