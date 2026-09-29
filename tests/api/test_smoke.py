"""Smoke tests: the smallest set that proves the environment is wired up.

Run these on every commit. If smoke fails, nothing else is worth running.
"""

import pytest

pytestmark = pytest.mark.smoke


class TestHealth:
    def test_products_endpoint_is_reachable(self, api_client):
        response = api_client.list_products(limit=1)

        assert response.status == 200, "core endpoint is down"

    def test_a_known_product_exists(self, api_client):
        product = api_client.get_product(1).json()

        assert product["id"] == 1
        assert product["title"], "product 1 must have a title"

    def test_ui_target_is_reachable(self, ui_page):
        response = ui_page.goto("/")

        assert response.status == 200, "UI target is down"
