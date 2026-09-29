"""Contract, boundary, negative and performance checks.

The suite is split by MARKER rather than by file, so you can run only the slice
of risk you need:

    pytest -m smoke              # quick health check
    pytest -m contract           # response shape guarantees
    pytest -m "not smoke"        # everything except the quick check
    pytest -m negative           # bad input handling
"""

import pytest

from config.settings import settings

REQUIRED_FIELDS = ("id", "title", "price", "category", "rating", "stock", "sku")


@pytest.mark.contract
class TestResponseContract:
    def test_every_product_field_is_present(self, api_client):
        product = api_client.get_product(1).json()

        missing = [f for f in REQUIRED_FIELDS if f not in product]
        assert not missing, f"missing fields: {missing}"

    def test_price_is_numeric(self, api_client):
        product = api_client.get_product(1).json()

        # Guards against a real regression class: a numeric field silently
        # becoming a string when a backend serializer changes.
        assert isinstance(product["price"], (int, float)), (
            f"price should be numeric, got {type(product['price']).__name__}"
        )

    def test_list_envelope_reports_total(self, api_client):
        payload = api_client.list_products(limit=2).json()

        assert payload["total"] > 2
        assert len(payload["products"]) == 2


@pytest.mark.negative
class TestBadInputHandling:
    @pytest.mark.parametrize("product_id", [999999, 0, -1])
    def test_unknown_ids_return_404(self, api_client, product_id):
        response = api_client.get_product(product_id)

        assert response.status == 404

    def test_invalid_limit_returns_400_with_a_reason(self, api_client):
        response = api_client.list_products(limit="abc")

        assert response.status == 400
        # An error code with no explanation is a poor API: the caller cannot
        # tell whether to fix the input or retry.
        assert response.json().get("message")

    def test_malformed_search_input_does_not_crash_the_service(self, api_client):
        response = api_client.search_products("' OR 1=1 --")

        # The worst possible outcome would be a 500. An empty 200 is correct.
        assert response.status == 200


@pytest.mark.performance
class TestPerformanceBudget:
    def test_read_endpoints_meet_the_latency_budget(self, api_client, timed_api_call):
        _, elapsed_ms = timed_api_call(api_client.get_product, 1)

        assert elapsed_ms < settings.api_budget_ms, (
            f"GET /products/1 took {elapsed_ms:.0f} ms, "
            f"over the {settings.api_budget_ms} ms budget"
        )

    def test_collection_endpoint_meets_the_latency_budget(self, api_client, timed_api_call):
        _, elapsed_ms = timed_api_call(api_client.list_products, limit=5)

        assert elapsed_ms < settings.api_budget_ms
