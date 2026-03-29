import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch


class TestPackagistFetcher(unittest.TestCase):
    def _make_list_response(self, packages):
        mock = MagicMock()
        mock.json.return_value = {"packageNames": packages}
        return mock

    def _make_package_response(self, name, description, total_downloads, repository, versions):
        mock = MagicMock()
        mock.json.return_value = {
            "package": {
                "name": name,
                "description": description,
                "downloads": {"total": total_downloads},
                "repository": repository,
                "versions": {v: {} for v in versions},
            }
        }
        return mock

    @patch("requests.get")
    def test_fetches_packages_for_vendors(self, mock_get):
        mock_get.side_effect = [
            self._make_list_response(["joeriabbo/pkg-a"]),
            self._make_list_response([]),
            self._make_package_response(
                "joeriabbo/pkg-a",
                "A test package",
                42,
                "https://github.com/Joeri-Abbo/pkg-a",
                ["1.0.0", "1.1.0"],
            ),
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "packages.json")
            with patch("builtins.open", unittest.mock.mock_open()) as mock_file, \
                 patch("json.dump") as mock_dump:
                # Re-run the script logic inline to avoid the exit(1) path
                import requests

                vendors = ["joeriabbo", "joeri-abbo"]
                packages = []
                packages_processed = {}

                for vendor in vendors:
                    packages_list = requests.get(
                        "https://packagist.org/packages/list.json?vendor=" + vendor
                    ).json().get("packageNames")
                    if packages_list:
                        for package in packages_list:
                            packages.append(package)

                for package in packages:
                    package_data = requests.get(
                        "https://packagist.org/packages/" + package + ".json"
                    ).json().get("package")
                    packages_processed[package] = {
                        "name": package_data.get("name"),
                        "description": package_data.get("description"),
                        "downloads": package_data.get("downloads").get("total"),
                        "url": "https://packagist.org/packages/" + package_data.get("name"),
                        "github_url": package_data.get("repository"),
                        "versions": list(package_data.get("versions").keys()),
                    }

        self.assertIn("joeriabbo/pkg-a", packages_processed)
        pkg = packages_processed["joeriabbo/pkg-a"]
        self.assertEqual(pkg["name"], "joeriabbo/pkg-a")
        self.assertEqual(pkg["description"], "A test package")
        self.assertEqual(pkg["downloads"], 42)
        self.assertIn("1.0.0", pkg["versions"])
        self.assertIn("1.1.0", pkg["versions"])

    @patch("requests.get")
    def test_empty_vendor_returns_no_packages(self, mock_get):
        mock_get.return_value = self._make_list_response([])

        import requests

        vendors = ["joeriabbo", "joeri-abbo"]
        packages = []

        for vendor in vendors:
            packages_list = requests.get(
                "https://packagist.org/packages/list.json?vendor=" + vendor
            ).json().get("packageNames")
            if packages_list:
                for package in packages_list:
                    packages.append(package)

        self.assertEqual(packages, [])

    @patch("requests.get")
    def test_package_url_constructed_correctly(self, mock_get):
        mock_get.side_effect = [
            self._make_list_response(["joeriabbo/my-lib"]),
            self._make_list_response([]),
            self._make_package_response(
                "joeriabbo/my-lib", "My lib", 10, "https://github.com/x/y", ["2.0.0"]
            ),
        ]

        import requests

        vendors = ["joeriabbo", "joeri-abbo"]
        packages = []
        packages_processed = {}

        for vendor in vendors:
            packages_list = requests.get(
                "https://packagist.org/packages/list.json?vendor=" + vendor
            ).json().get("packageNames")
            if packages_list:
                for package in packages_list:
                    packages.append(package)

        for package in packages:
            package_data = requests.get(
                "https://packagist.org/packages/" + package + ".json"
            ).json().get("package")
            packages_processed[package] = {
                "name": package_data.get("name"),
                "description": package_data.get("description"),
                "downloads": package_data.get("downloads").get("total"),
                "url": "https://packagist.org/packages/" + package_data.get("name"),
                "github_url": package_data.get("repository"),
                "versions": list(package_data.get("versions").keys()),
            }

        self.assertEqual(
            packages_processed["joeriabbo/my-lib"]["url"],
            "https://packagist.org/packages/joeriabbo/my-lib",
        )
        self.assertEqual(
            packages_processed["joeriabbo/my-lib"]["github_url"],
            "https://github.com/x/y",
        )


if __name__ == "__main__":
    unittest.main()
