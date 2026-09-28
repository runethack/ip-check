import argparse
import json
import ipaddress
from typing import Dict, Any, List, Optional, Iterable

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None


class IPChecker:
    """Validate and analyze IPv4/IPv6 addresses."""

    @staticmethod
    def is_valid_ip(value: str) -> bool:
        if not value or not isinstance(value, str):
            return False
        try:
            ipaddress.ip_address(value.strip())
            return True
        except ValueError:
            return False

    @staticmethod
    def get_ip_version(value: str) -> Optional[int]:
        if not IPChecker.is_valid_ip(value):
            return None
        return ipaddress.ip_address(value.strip()).version

    @staticmethod
    def normalize_ip(value: str) -> Optional[str]:
        if not IPChecker.is_valid_ip(value):
            return None
        return str(ipaddress.ip_address(value.strip()))

    @staticmethod
    def is_private_ip(value: str) -> bool:
        ip = IPChecker._parse_ip(value)
        return bool(ip and ip.is_private)

    @staticmethod
    def is_public_ip(value: str) -> bool:
        ip = IPChecker._parse_ip(value)
        if ip is None:
            return False
        return not (
            ip.is_private
            or ip.is_loopback
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
            or ip.is_link_local
        )

    @staticmethod
    def is_reserved_ip(value: str) -> bool:
        ip = IPChecker._parse_ip(value)
        return bool(ip and (ip.is_reserved or ip.is_multicast or ip.is_unspecified))

    @staticmethod
    def is_loopback_ip(value: str) -> bool:
        ip = IPChecker._parse_ip(value)
        return bool(ip and ip.is_loopback)

    @staticmethod
    def _parse_ip(value: str):
        if not value or not isinstance(value, str):
            return None
        try:
            return ipaddress.ip_address(value.strip())
        except ValueError:
            return None

    @staticmethod
    def validate(value: str) -> Dict[str, Any]:
        ip = IPChecker._parse_ip(value)
        result = {
            "input": value,
            "is_valid": bool(ip),
            "version": None,
            "normalized": None,
            "is_private": False,
            "is_public": False,
            "is_reserved": False,
            "is_loopback": False,
            "is_multicast": False,
            "is_link_local": False,
            "is_unspecified": False,
        }

        if not ip:
            return result

        result["version"] = ip.version
        result["normalized"] = str(ip)
        result["is_private"] = ip.is_private
        result["is_public"] = IPChecker.is_public_ip(str(ip))
        result["is_reserved"] = bool(ip.is_reserved or ip.is_multicast or ip.is_unspecified)
        result["is_loopback"] = ip.is_loopback
        result["is_multicast"] = ip.is_multicast
        result["is_link_local"] = ip.is_link_local
        result["is_unspecified"] = ip.is_unspecified

        return result

    @staticmethod
    def _fetch_json(url: str, timeout: int = 5) -> Optional[Dict[str, Any]]:
        if requests is None:
            return None
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code != 200:
                return None
            return response.json()
        except Exception:
            return None

    @staticmethod
    def check_ip_services(ip: str, timeout: int = 5) -> List[Dict[str, Any]]:
        """Check IP using public services when available."""
        if not IPChecker.is_valid_ip(ip):
            return []

        services = [
            {
                "name": "ipapi",
                "url": f"http://ip-api.com/json/{ip}",
            },
            {
                "name": "ipwho",
                "url": f"https://ipwho.is/{ip}?output=json",
            },
            {
                "name": "ifconfig",
                "url": f"https://ifconfig.co/json?ip={ip}",
            },
        ]

        results = []
        for service in services:
            raw = IPChecker._fetch_json(service["url"], timeout=timeout)
            if raw is None:
                results.append({
                    "service": service["name"],
                    "status": "unavailable",
                    "data": None,
                })
                continue

            payload = {
                "service": service["name"],
                "status": "ok",
                "data": raw,
            }
            if isinstance(raw, dict):
                if raw.get("status") == "fail":
                    payload["status"] = "fail"
                elif raw.get("success") is False:
                    payload["status"] = "fail"
            results.append(payload)

        return results

    @staticmethod
    def validate_file(file_path: str, timeout: int = 5) -> List[Dict[str, Any]]:
        """Validate multiple IPs from a file, one IP per line."""
        results = []
        try:
            with open(file_path, "r", encoding="utf-8") as fh:
                for line in fh:
                    value = line.strip()
                    if not value:
                        continue
                    item = IPChecker.validate(value)
                    item["service_checks"] = IPChecker.check_ip_services(value, timeout=timeout)
                    results.append(item)
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        return results


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and analyze IP addresses.")
    parser.add_argument("--ip", help="IP address to validate")
    parser.add_argument("--file", help="Path to a text file with one IP per line")
    parser.add_argument("--json", action="store_true", help="Print result as JSON")
    parser.add_argument("--services", action="store_true", help="Check public services for IP metadata")
    parser.add_argument("--timeout", type=int, default=5, help="Timeout for external service calls in seconds")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.file:
        results = IPChecker.validate_file(args.file, timeout=args.timeout)
        if args.json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            for entry in results:
                print(f"IP: {entry['input']} | Valid: {entry['is_valid']} | Type: {entry['normalized']}")
                if args.services:
                    for service in entry.get("service_checks", []):
                        print(f"  - {service['service']}: {service['status']}")
        return

    if not args.ip:
        parser.error("You must provide either --ip or --file")

    result = IPChecker.validate(args.ip)
    if args.services:
        result["service_checks"] = IPChecker.check_ip_services(args.ip, timeout=args.timeout)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"IP: {args.ip}")
        print(f"Valid: {result['is_valid']}")
        print(f"Version: {result['version']}")
        print(f"Normalized: {result['normalized']}")
        print(f"Private: {result['is_private']}")
        print(f"Public: {result['is_public']}")
        print(f"Reserved: {result['is_reserved']}")
        print(f"Loopback: {result['is_loopback']}")
        if args.services:
            print("Service checks:")
            for item in result.get("service_checks", []):
                print(f"  - {item['service']}: {item['status']}")


if __name__ == "__main__":
    main()
