"""Reusable API client.

Compared with repo 2's client, this one is built to be configuration-driven and
to log every call, which is what you want once a framework is used by a team
rather than a single person.
"""

from utils.logger import logger


class ApiResponse:
    def __init__(self, raw, base_url):
        self.raw = raw
        self.base_url = base_url

    @property
    def status(self):
        return self.raw.status

    @property
    def headers(self):
        return self.raw.headers

    def json(self):
        return self.raw.json()

    def text(self):
        return self.raw.text()

    def __repr__(self):
        return f"<ApiResponse {self.status} {self.raw.url}>"


class ApiClient:
    def __init__(self, request, base_url):
        self.base_url = base_url
        self.context = request.new_context(
            base_url=base_url,
            extra_http_headers={"Accept": "application/json"},
        )

    def close(self):
        self.context.dispose()

    def _send(self, method, path, **kwargs):
        logger.info("API %s %s", method.upper(), path)
        # Dispatch to the matching method on the Playwright context
        # (context.get, context.post, ...). Passing the method name as a string
        # avoids writing the same logging code four times.
        caller = getattr(self.context, method.lower())
        raw = caller(path, **kwargs)
        response = ApiResponse(raw, self.base_url)
        logger.info("API %s %s -> %s", method.upper(), path, response.status)
        return response

    # Products
    def list_products(self, **params):
        return self._send("GET", "/products", params=params)

    def get_product(self, product_id):
        return self._send("GET", f"/products/{product_id}")

    def search_products(self, query):
        return self._send("GET", "/products/search", params={"q": query})

    def create_product(self, payload):
        return self._send("POST", "/products/add", data=payload)

    def update_product(self, product_id, payload):
        return self._send("PUT", f"/products/{product_id}", data=payload)

    def delete_product(self, product_id):
        return self._send("DELETE", f"/products/{product_id}")
