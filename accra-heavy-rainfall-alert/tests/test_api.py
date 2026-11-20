"""Tests for the web API. They are skipped if FastAPI or httpx is not installed."""
import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

from api.main import create_app  # noqa: E402


@pytest.fixture
def client(service):
    """A test client that uses the small test files."""
    return TestClient(create_app(service))


def test_health_reports_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_periods_gives_the_range(client):
    body = client.get("/periods").json()
    assert body["first"] < body["last"]
    assert body["count"] == 120


def test_predict_returns_a_band_and_a_past_rate(client):
    response = client.get("/predict", params={"period": "2000-02-11"})
    assert response.status_code == 200
    body = response.json()
    assert body["risk_band"] in {"Low", "Typical", "High"}
    assert 0 <= body["past_heavy_rain_rate"] <= 1
    assert "does not detect floods" in body["note"]


def test_predict_unknown_period_is_404(client):
    assert client.get("/predict", params={"period": "1900-01-01"}).status_code == 404


def test_predict_bad_date_is_422(client):
    assert client.get("/predict", params={"period": "not-a-date"}).status_code == 422


def test_importances_lists_every_input(client):
    body = client.get("/importances").json()
    assert len(body) == 10
    assert abs(sum(item["share"] for item in body) - 1.0) < 1e-6
