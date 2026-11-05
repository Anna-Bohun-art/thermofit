import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _demo_csv(kind):
    return client.get(f"/api/demo/{kind}").json()["csv"]


def test_health():
    assert client.get("/api/health").json() == {"status": "ok"}


def test_dsc_two_state_roundtrip():
    csv = _demo_csv("dsc_two_state")
    r = client.post("/api/fit/dsc", files={"file": ("d.csv", csv)}, data={"model": "two_state"})
    assert r.status_code == 200
    body = r.json()
    tm = next(p for p in body["params"] if p["name"] == "Tm")
    assert tm["value"] == pytest.approx(45.3, abs=0.2)
    assert body["r2"] > 0.99
    assert len(body["x_fit"]) == len(body["y_fit"])


def test_dsc_irreversible_roundtrip():
    csv = _demo_csv("dsc_irreversible")
    r = client.post(
        "/api/fit/dsc", files={"file": ("d.csv", csv)},
        data={"model": "irreversible", "scan_rate": "1.0"},
    )
    assert r.status_code == 200
    assert r.json()["r2"] > 0.99


def test_irreversible_without_scan_rate_is_422():
    csv = _demo_csv("dsc_irreversible")
    r = client.post("/api/fit/dsc", files={"file": ("d.csv", csv)}, data={"model": "irreversible"})
    assert r.status_code == 422


def test_semicolon_csv_is_accepted():
    csv = _demo_csv("dsc_two_state").replace(",", ";")
    r = client.post("/api/fit/dsc", files={"file": ("d.csv", csv)}, data={"model": "two_state"})
    assert r.status_code == 200


def test_garbage_file_gives_400():
    r = client.post("/api/fit/dsc", files={"file": ("d.csv", "hello world")}, data={"model": "two_state"})
    assert r.status_code in (400, 422)  # unparsable, or parsed but too few points


def test_unknown_model_is_422():
    csv = _demo_csv("dsc_two_state")
    r = client.post("/api/fit/dsc", files={"file": ("d.csv", csv)}, data={"model": "magic"})
    assert r.status_code == 422


def test_oversized_upload_is_413():
    big = "a,b\n" + "1,2\n" * 600_000
    r = client.post("/api/fit/dsc", files={"file": ("d.csv", big)}, data={"model": "two_state"})
    assert r.status_code == 413


def test_removed_michaelis_menten_endpoint_is_gone():
    assert client.post("/api/fit/michaelis-menten", files={"file": ("d.csv", "a,b\n1,2\n")}).status_code == 404
    assert client.get("/api/demo/michaelis_menten").status_code == 404


def test_unknown_demo_is_404():
    assert client.get("/api/demo/nope").status_code == 404


def test_thesis_demo_carries_source_and_is_not_flagged_synthetic():
    body = client.get("/api/demo/thesis_zn").json()
    assert body["synthetic"] is False
    assert "Fig. 6" in body["source"]
    r = client.post("/api/fit/dsc", files={"file": ("d.csv", body["csv"])}, data={"model": "two_state"})
    assert r.status_code == 200
    tm = next(p for p in r.json()["params"] if p["name"] == "Tm")
    assert tm["value"] == pytest.approx(45.3, abs=0.1)


def test_thesis_fe_demo_returns_scan_rate_and_fits_irreversible():
    body = client.get("/api/demo/thesis_fe_1p0").json()
    assert body["scan_rate"] == 1.0 and body["synthetic"] is False and "Fig. 7" in body["source"]
    r = client.post(
        "/api/fit/dsc", files={"file": ("d.csv", body["csv"])},
        data={"model": "irreversible", "scan_rate": str(body["scan_rate"])},
    )
    assert r.status_code == 200
    ts = next(p for p in r.json()["params"] if p["name"].startswith("T*"))
    assert ts["value"] - 273.15 == pytest.approx(43.1, abs=0.15)
