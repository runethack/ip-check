import unittest

from ip_checker import IPChecker


class TestIPChecker(unittest.TestCase):
    def test_valid_ipv4(self):
        self.assertTrue(IPChecker.is_valid_ip("8.8.8.8"))
        self.assertTrue(IPChecker.is_valid_ip("192.168.1.10"))

    def test_valid_ipv6(self):
        self.assertTrue(IPChecker.is_valid_ip("2001:4860:4860::8888"))
        self.assertTrue(IPChecker.is_valid_ip("::1"))

    def test_invalid_ip(self):
        self.assertFalse(IPChecker.is_valid_ip("999.999.999.999"))
        self.assertFalse(IPChecker.is_valid_ip("not-an-ip"))
        self.assertFalse(IPChecker.is_valid_ip(""))

    def test_private_public(self):
        self.assertTrue(IPChecker.is_private_ip("192.168.1.10"))
        self.assertFalse(IPChecker.is_private_ip("8.8.8.8"))
        self.assertTrue(IPChecker.is_public_ip("8.8.8.8"))
        self.assertFalse(IPChecker.is_public_ip("127.0.0.1"))

    def test_validate_output(self):
        result = IPChecker.validate("8.8.8.8")
        self.assertTrue(result["is_valid"])
        self.assertEqual(result["version"], 4)
        self.assertEqual(result["normalized"], "8.8.8.8")

    def test_loopback_and_reserved(self):
        self.assertTrue(IPChecker.is_loopback_ip("127.0.0.1"))
        self.assertTrue(IPChecker.is_reserved_ip("224.0.0.1"))


if __name__ == "__main__":
    unittest.main()
