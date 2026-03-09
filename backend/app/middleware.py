import ipaddress
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings


def _parse_allowed_networks(raw: str) -> list:
    """Parse a comma-separated string of IPs/CIDRs into network objects.

    Both single host addresses (e.g. ``192.168.1.1``) and CIDR notation
    (e.g. ``10.0.0.0/8``) are accepted.  ``strict=False`` means a host
    address with a subnet mask (e.g. ``192.168.1.5/24``) is normalised to
    its network address (``192.168.1.0/24``) rather than raising an error.
    A plain host address becomes a /32 (IPv4) or /128 (IPv6) network.
    """
    networks = []
    for entry in raw.split(","):
        entry = entry.strip()
        if not entry:
            continue
        networks.append(ipaddress.ip_network(entry, strict=False))
    return networks


def _is_ip_allowed(client_ip: str, networks: list) -> bool:
    """Return True if client_ip is within any of the allowed networks."""
    try:
        addr = ipaddress.ip_address(client_ip)
    except ValueError:
        return False
    return any(addr in network for network in networks)


def _get_client_ip(request: Request) -> str:
    """Extract the real client IP from the request.

    ``X-Forwarded-For`` is only consulted when ``TRUST_FORWARDED_FOR=true``
    is set in the environment.  Trusting this header without verifying that
    the request actually comes from a known proxy would allow an attacker to
    spoof their IP and bypass the whitelist.
    """
    if settings.trust_forwarded_for:
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # The header may contain multiple IPs; the first is the original client.
            return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return ""


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """Block requests from IP addresses not in the configured whitelist.

    If ``ALLOWED_IPS`` is empty (the default) all addresses are permitted,
    preserving backwards-compatible open access.
    """

    def __init__(self, app):
        super().__init__(app)
        self._networks = _parse_allowed_networks(settings.allowed_ips)

    async def dispatch(self, request: Request, call_next):
        # No restriction when the whitelist is empty.
        if not self._networks:
            return await call_next(request)

        client_ip = _get_client_ip(request)
        if not _is_ip_allowed(client_ip, self._networks):
            return JSONResponse(
                status_code=403,
                content={"detail": f"Tilgang nektet for IP-adresse: {client_ip}"},
            )

        return await call_next(request)
