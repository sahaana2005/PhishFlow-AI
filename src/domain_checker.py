
from urllib.parse import urlsplit


# Exact hostnames only.
# Add domains here only after independently verifying them.
TRUSTED_HOSTS = {
    "github.com",
}


def check_trusted_domain(url):
    """
    Check whether a URL belongs to an explicitly trusted hostname.

    This is a hostname match, not a guarantee that every page
    or resource on the website is safe.
    """

    try:
        parsed = urlsplit(url.strip())
        hostname = parsed.hostname

        if not hostname:
            return False

        hostname = hostname.lower().rstrip(".")

        return hostname in TRUSTED_HOSTS

    except (ValueError, AttributeError):
        return False
