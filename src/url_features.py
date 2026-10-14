
from urllib.parse import urlsplit
import ipaddress


def extract_url_features(url):
    """Validate an HTTP(S) URL and extract basic characteristics."""

    # 1. Check the input type
    if not isinstance(url, str):
        raise ValueError("URL must be provided as text.")

    # 2. Remove unnecessary spaces at the beginning and end
    url = url.strip()

    # 3. Reject empty input
    if not url:
        raise ValueError("URL cannot be empty.")

    # 4. Parse the URL
    try:
        parsed = urlsplit(url)
    except ValueError as error:
        raise ValueError("Malformed URL.") from error

    # 5. Allow only HTTP and HTTPS
    if parsed.scheme.lower() not in ("http", "https"):
        raise ValueError("Only HTTP and HTTPS URLs are supported.")

    # 6. Require a hostname
    try:
        hostname = parsed.hostname
        parsed.port  # Accessing this also detects invalid port numbers.
    except ValueError as error:
        raise ValueError("Invalid hostname or port.") from error

    if not hostname:
        raise ValueError("URL must contain a hostname.")

    # 7. Extract features
    uses_https = parsed.scheme.lower() == "https"
    url_length = len(url)
    has_at_symbol = "@" in url

    # 8. Check whether the hostname is an IP address
    try:
        ipaddress.ip_address(hostname)
        host_is_ip = True
    except ValueError:
        host_is_ip = False

    return {
        "url_length": url_length,
        "uses_https": uses_https,
        "has_at_symbol": has_at_symbol,
        "host_is_ip": host_is_ip,
    }


if __name__ == "__main__":
    sample_url = "http://192.168.1.10/login"

    try:
        features = extract_url_features(sample_url)
        print("URL:", sample_url)
        print("Extracted features:", features)
    except ValueError as error:
        print("Input error:", error)
