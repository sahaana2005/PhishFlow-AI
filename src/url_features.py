
from urllib.parse import urlsplit
import ipaddress


def extract_url_features(url):
    """Validate an HTTP(S) URL and extract numerical phishing indicators."""

    if not isinstance(url, str):
        raise ValueError("URL must be text.")

    url = url.strip()

    if not url:
        raise ValueError("URL cannot be empty.")

    try:
        parsed = urlsplit(url)
    except ValueError as error:
        raise ValueError("Invalid URL format.") from error

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
    path = parsed.path.lower()
    full_url = url.lower()

    try:
        ipaddress.ip_address(hostname)
        host_is_ip = 1
    except ValueError:
        host_is_ip = 0

    hostname_labels = hostname.split(".")

    suspicious_keywords = (
        "login", "verify", "account", "password"
    )

    shortener_domains = {
        "bit.ly", "is.gd", "t.co", "tinyurl.com",
        "ow.ly", "buff.ly", "cutt.ly", "rebrand.ly"
    }

    return {
        # Existing features
        "url_length": len(url),
        "uses_https": int(parsed.scheme.lower() == "https"),
        "has_at_symbol": int("@" in url),
        "host_is_ip": host_is_ip,
        "subdomain_count": (
            0 if host_is_ip
            else max(0, len(hostname_labels) - 2)
        ),
        "has_hyphen_in_hostname": int("-" in hostname),
        "uses_url_shortener": int(hostname in shortener_domains),
        "matched_keyword_count": sum(
            keyword in full_url for keyword in suspicious_keywords
        ),
        "hostname_length": len(hostname),
        "path_length": len(parsed.path),
        "hostname_digit_count": sum(
            character.isdigit() for character in hostname
        ),

        # New features
        "keyword_in_hostname": int(
            any(keyword in hostname for keyword in suspicious_keywords)
        ),
        "keyword_in_path": int(
            any(keyword in path for keyword in suspicious_keywords)
        ),
        "has_query_parameters": int(bool(parsed.query)),
        "has_fragment": int(bool(parsed.fragment)),
        "hostname_label_count": len(hostname_labels),
    }
