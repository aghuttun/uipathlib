"""Smoke tests for the public Python surface of the Rust extension module."""

import unittest

import uipathlib


class SmokeTests(unittest.TestCase):
    """Validate minimal public API symbols and methods."""

    def test_public_api_symbols_exist(self):
        self.assertTrue(hasattr(uipathlib, "UiPath"))
        self.assertTrue(hasattr(uipathlib, "Response"))

    def test_uipath_exposes_expected_methods(self):
        expected_methods = [
            "is_auth",
            "auth",
            "list_assets",
            "list_buckets",
            "create_bucket",
            "delete_bucket",
            "upload_bucket_file",
            "delete_bucket_file",
            "list_calendars",
            "list_environments",
            "list_jobs",
            "start_job",
            "stop_job",
            "list_machines",
            "list_processes",
            "list_queues",
            "list_queue_items",
            "get_queue_item",
            "add_queue_item",
            "update_queue_item",
            "delete_queue_item",
            "list_releases",
            "list_robots",
            "list_robot_logs",
            "list_roles",
            "list_schedules",
            "list_sessions",
        ]

        for method_name in expected_methods:
            with self.subTest(method=method_name):
                self.assertTrue(hasattr(uipathlib.UiPath, method_name))


if __name__ == "__main__":
    unittest.main()
