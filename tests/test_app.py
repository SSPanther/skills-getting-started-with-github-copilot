import pytest

from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # Make a shallow copy of initial participants so tests don't leak state between runs
    original = {
        name: dict(details, participants=list(details.get("participants", [])))
        for name, details in activities.items()
    }
    yield
    # restore
    for name, details in original.items():
        activities[name]["participants"] = list(details.get("participants", []))


def test_get_activities():
    client = TestClient(app)
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data


def test_signup_and_duplicate_signup():
    client = TestClient(app)
    activity = "Chess Club"
    email = "pytest_user@example.com"

    # sign up successfully
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]

    # duplicate signup should fail
    resp2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp2.status_code == 400


def test_unregister_participant_and_not_found():
    client = TestClient(app)
    activity = "Programming Class"
    email = "temp-remove@example.com"

    # ensure not present then sign up
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]

    # unregister
    resp2 = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp2.status_code == 200
    assert email not in activities[activity]["participants"]

    # unregistering again should return 404
    resp3 = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp3.status_code == 404
