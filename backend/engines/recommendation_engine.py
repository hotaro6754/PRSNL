from typing import List


class RecommendationEngine:
    """Threat-specific safe browsing recommendations."""

    _RECOMMENDATIONS = {
        "CREDENTIAL_HARVESTING": [
            "Do not enter your password or any login credentials on this page.",
            "Close the page immediately and do not interact further.",
            "Navigate manually to the official website by typing the URL yourself.",
            "If you already entered credentials, change your password immediately through the official service.",
            "Enable two-factor authentication on all important accounts.",
            "Report this page to the service being impersonated.",
        ],
        "PHISHING": [
            "Do not click any links in this message.",
            "Do not provide personal information or credentials.",
            "Verify the sender through an official, independent channel.",
            "If you suspect impersonation, contact the real organization directly.",
            "Report the suspicious content to your security team.",
        ],
        "URL_PHISHING": [
            "Do not visit this URL or enter any data.",
            "The URL may be designed to steal your information.",
            "Verify the intended service through its official domain.",
            "Report this URL to your browser's safe browsing service.",
        ],
        "FINANCIAL_FRAUD": [
            "Do not transfer money or approve any payment requests.",
            "Do not share banking credentials, UPI PINs, or OTPs.",
            "Do not approve unknown payment requests on your banking app.",
            "Contact your financial institution through its official channel.",
            "File a fraud complaint with your bank if you already transacted.",
        ],
        "SOCIAL_ENGINEERING": [
            "Take a moment to think before responding to urgent requests.",
            "Verify the identity of the sender through a separate channel.",
            "Do not bypass standard procedures regardless of claimed authority.",
            "Consult with a colleague or supervisor before taking action.",
        ],
        "MALWARE": [
            "Do not download or execute any attachments from this source.",
            "Do not enable macros or allow unknown scripts to run.",
            "Run a full system antivirus scan if you opened anything.",
            "Report the incident to your IT security team immediately.",
            "Disconnect from the network if you suspect infection.",
        ],
        "IMPERSONATION": [
            "Verify the sender's identity through official channels.",
            "Do not trust sender IDs in SMS - they can be spoofed.",
            "Check email headers for domain mismatches.",
            "Contact the organization being impersonated to report the attempt.",
        ],
        "URL_OBFUSCATION": [
            "Do not visit URLs that appear to be deliberately obscured.",
            "Check the actual destination before clicking shortened URLs.",
            "Use a URL preview service to inspect shortened links.",
            "Report obfuscated URLs to your security team.",
        ],
        "URL_SECURITY": [
            "Avoid entering sensitive data on HTTP (non-HTTPS) pages.",
            "Verify the site's SSL certificate before submitting information.",
            "Use a VPN when accessing sensitive sites on public networks.",
        ],
        "URL_REPUTATION": [
            "Exercise caution with websites using unusual domain extensions.",
            "Verify the site's legitimacy before interacting.",
            "Check reviews or reputation scores before trusting a new site.",
        ],
        "BRAND_ABUSE": [
            "Verify the URL domain matches the official brand website.",
            "Look for subtle misspellings in the domain name.",
            "Report brand impersonation to the legitimate company.",
        ],
        "SUSPICIOUS": [
            "Exercise caution with this content.",
            "Do not provide personal information without verification.",
            "Report suspicious behavior to your security team.",
        ],
    }

    def get_recommendations(self, threat_type: str, classification: str, input_type: str) -> List[str]:
        if classification == "SAFE":
            return [
                "No major suspicious indicators were detected.",
                "A low-risk result does not guarantee that content is completely safe.",
                "Continue to exercise normal caution when interacting online.",
                "Keep your software and security tools up to date.",
            ]

        if classification == "UNVERIFIED":
            return [
                "The system could not confidently analyze this content.",
                "Do not interact with the content until it can be verified.",
                "Try submitting the content again or use an alternative analysis tool.",
                "Report the content if you believe it may be suspicious.",
            ]

        # Lookup by threat type (case-insensitive)
        key = threat_type.upper().replace(" ", "_")
        recs = self._RECOMMENDATIONS.get(key)
        if recs:
            return recs

        # Fallback by input type
        _INPUT_FALLBACKS = {
            "sms": [
                "Do not use any links in this message.",
                "Verify claims using the official app or website.",
                "Do not share OTPs or verification codes with anyone.",
                "Block and report the sender.",
            ],
            "email": [
                "Do not open attachments from this sender.",
                "Verify the sender independently before responding.",
                "Do not enable macros or unknown scripts.",
                "Report the email as phishing in your email client.",
            ],
            "qr": [
                "Do not scan unknown QR codes from untrusted sources.",
                "Inspect the destination URL before continuing.",
                "Verify the destination using an official source.",
                "Do not approve unexpected payments from QR scans.",
            ],
        }
        if input_type in _INPUT_FALLBACKS:
            return _INPUT_FALLBACKS[input_type]

        return [
            "Exercise extreme caution with this content.",
            "Do not provide personal or financial information.",
            "Avoid interacting with suspicious content.",
            "Report this content to your security team.",
        ]
