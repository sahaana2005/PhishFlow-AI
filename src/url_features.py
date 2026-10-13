
from urllib.parse import urlsplit
import ipaddress


def extract_url_features(url):
    """Extract basic characteristics from a URL."""

    parsed = urlsplit(url.strip())

    # Check whether the URL uses HTTPS
    uses_https = parsed.scheme.lower() == "https"

    # Count the characters in the URL
    url_length = len(url.strip())

    # Check for suspicious-looking symbols
    has_at_symbol = "@" in url

    # Check whether the hostname is an IP address
    hostname = parsed.hostname or ""
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
    test_url = "http://192.168.1.10/login"
    features = extract_url_features(test_url)

    print("URL:", test_url)
    print("Extracted features:")

    for feature, value in features.items():
        print(f"{feature}: {value}")
