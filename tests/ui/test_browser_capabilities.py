"""UI tests for the framework's browser layer.

The app under test is bundled in demo_app/ and served locally by a session
fixture, so these tests are deterministic: no third-party site can break them
overnight, and a failure always means the code changed.

The point of this file is to prove the framework's browser capabilities work:
JS execution, viewport control, timing, and evidence capture.
"""

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.ui


class TestPageLoads:
    def test_navigation_returns_ok(self, ui_page):
        response = ui_page.goto("/")

        assert response.status == 200

    def test_page_has_a_visible_heading(self, ui_page):
        ui_page.goto("/")

        expect(ui_page.locator("h1")).to_be_visible()
        expect(ui_page.locator("h1")).to_have_text("Framework Demo App")

    def test_title_is_not_empty(self, ui_page):
        ui_page.goto("/")

        assert ui_page.title().strip(), "every page should have a title"


class TestJavaScriptExecution:
    def test_javascript_is_enabled(self, ui_page):
        ui_page.goto("/")

        # Guards against a suite that passes with JS disabled locally and then
        # behaves completely differently in CI. A 2 here proves the runtime is
        # live.
        assert ui_page.evaluate("() => 1 + 1") == 2

    def test_dom_updates_in_response_to_a_click(self, ui_page):
        ui_page.goto("/")

        details = ui_page.locator("#details")
        expect(details).to_be_hidden()

        ui_page.locator("#toggle-button").click()

        expect(details).to_be_visible()
        expect(details).to_have_text("These details were revealed by JavaScript.")


class TestFormValidation:
    def test_invalid_email_is_rejected(self, ui_page):
        ui_page.goto("/")
        ui_page.locator("#email").fill("not-an-email")
        ui_page.locator("#submit-button").click()

        expect(ui_page.locator("#email-error")).to_be_visible()
        expect(ui_page.locator("#signup-success")).to_be_hidden()

    def test_valid_email_is_accepted(self, ui_page):
        ui_page.goto("/")
        ui_page.locator("#email").fill("tester@example.com")
        ui_page.locator("#submit-button").click()

        expect(ui_page.locator("#signup-success")).to_be_visible()


class TestBrowserCapabilities:
    def test_user_agent_is_reported(self, ui_page):
        ui_page.goto("/")

        assert "Mozilla" in ui_page.evaluate("() => navigator.userAgent")

    def test_viewport_change_actually_applies(self, ui_page):
        ui_page.set_viewport_size({"width": 375, "height": 812})
        ui_page.goto("/")

        # Responsive checks are worthless if the viewport never changed, which
        # is why this verifies the value rather than assuming it.
        assert ui_page.evaluate("() => window.innerWidth") == 375

    def test_screenshot_is_captured_as_evidence(self, ui_page, tmp_path):
        ui_page.goto("/")
        target = tmp_path / "homepage.png"
        ui_page.screenshot(path=str(target), full_page=True)

        # A very small file means the capture silently produced nothing, which
        # would otherwise only be noticed when someone opens the evidence.
        assert target.exists()
        assert target.stat().st_size > 1000, "screenshot looks empty"

    def test_failed_expectation_reports_a_useful_locator(self, ui_page):
        ui_page.goto("/")

        # A useful error message names the locator that was not found. This
        # keeps the suite debuggable as it grows.
        with pytest.raises(AssertionError) as failure:
            expect(ui_page.locator("#does-not-exist")).to_be_visible(timeout=1500)

        assert "does-not-exist" in str(failure.value)
