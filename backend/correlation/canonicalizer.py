import urllib.parse
import re

class Canonicalizer:
    @staticmethod
    def normalize_url(url: str) -> str:
        """
        Normalizes a URL:
        - Lowercases scheme and host
        - Strips default ports (80 for http, 443 for https)
        - Normalizes paths (e.g. removing trailing slashes except for root, collapsing redundant slashes)
        """
        if not url:
            return url
            
        # Ensure it has a scheme to be parseable
        has_scheme = "://" in url
        if not has_scheme:
            url = "http://" + url
            
        parsed = urllib.parse.urlsplit(url)
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()
        path = parsed.path
        query = parsed.query
        fragment = parsed.fragment

        # Strip default ports
        if ":" in netloc:
            host, port = netloc.rsplit(":", 1)
            if (scheme == "http" and port == "80") or (scheme == "https" and port == "443"):
                netloc = host

        # Normalize path
        if not path:
            path = "/"
        else:
            # Collapse redundant slashes
            path = re.sub(r'/+', '/', path)
            # Remove trailing slash if not root
            if len(path) > 1 and path.endswith("/"):
                path = path[:-1]

        normalized_url = urllib.parse.urlunsplit((scheme, netloc, path, query, fragment))
        
        # If we added a scheme just for parsing, we should keep it because a valid URL must have a scheme.
        return normalized_url

    @staticmethod
    def normalize_email(email: str) -> str:
        """
        Normalizes an email address:
        - Trims whitespace
        - Lowercases the whole address
        """
        if not email:
            return email
            
        email = email.strip().lower()
        return email

    @staticmethod
    def normalize_domain(domain: str) -> str:
        """
        Normalizes a domain:
        - Trims whitespace
        - Lowercases
        - Removes trailing dot
        """
        if not domain:
            return domain
            
        domain = domain.strip().lower()
        if domain.endswith("."):
            domain = domain[:-1]
        
        # Remove scheme if someone passed a URL as domain accidentally
        if "://" in domain:
            domain = domain.split("://")[-1]
            
        # Remove path
        if "/" in domain:
            domain = domain.split("/")[0]
            
        # Remove port
        if ":" in domain:
            domain = domain.split(":")[0]
            
        return domain
