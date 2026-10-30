import ipaddress
from urllib.parse import urlparse

# Words often used to pressure people into clicking
SUSPICIOUS_WORDS = ["login", "verify", "update", "secure", "account",
                    "bank", "password", "confirm", "kyc", "otp"]

# Services that hide the real destination behind a short link
SHORTENERS = ["bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd", "cutt.ly"]


def extract_features(url):
    """Turn one URL (plain text) into a dictionary of simple features.
    This function only reads the text. It never opens the URL."""
    url = (url or "").strip()
    if not url:
        return None

    # Add a scheme if missing, so the parser can find the host
    if "://" not in url:
        url = "http://" + url

    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
    except ValueError:
        return None  # malformed URL

    if not host:
        return None

    # Is the host a raw IP address like 192.168.1.1?
    try:
        ipaddress.ip_address(host)
        is_ip = True
    except ValueError:
        is_ip = False

    lowered = url.lower()
    return {
        "url_length": len(url),
        "uses_https": parsed.scheme == "https",
        "host_is_ip": is_ip,
        "dot_count_in_host": host.count("."),
        "hyphen_count_in_host": host.count("-"),
        "digit_count": sum(ch.isdigit() for ch in url),
        "has_at_symbol": "@" in url,
        "has_punycode": "xn--" in host,
        "is_shortener": host in SHORTENERS,
        "suspicious_word_count": sum(word in lowered for word in SUSPICIOUS_WORDS),
    }


if __name__ == "__main__":
    # Plain text examples only. Nothing here is ever opened.
    examples = [
        "https://www.example.com/about",
        "http://192.168.1.1/login/verify-account",
        "http://secure-update-account.example.net/login@verify",
        "https://bit.ly/abc123",
        "",
        "http://[bad-url",
    ]
    for url in examples:
        print("URL:", repr(url))
        features = extract_features(url)
        if features is None:
            print("  -> could not analyse (empty or malformed input)")
        else:
            for name, value in features.items():
                print(f"  {name}: {value}")
        print()