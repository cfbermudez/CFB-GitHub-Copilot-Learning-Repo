from src import app as app_module


def test_get_activities_returns_expected_structure(client):
    # Arrange
    expected_keys = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

    first_activity = data["Chess Club"]
    assert expected_keys.issubset(first_activity.keys())
    assert isinstance(first_activity["participants"], list)


def test_signup_adds_participant_and_preserves_other_activities(client):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    before_count = len(app_module.activities[activity_name]["participants"])
    other_activity_before = list(app_module.activities["Gym Class"]["participants"])

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in app_module.activities[activity_name]["participants"]
    assert len(app_module.activities[activity_name]["participants"]) == before_count + 1
    assert app_module.activities["Gym Class"]["participants"] == other_activity_before


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"
    before_snapshot = list(app_module.activities[activity_name]["participants"])

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": existing_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert app_module.activities[activity_name]["participants"] == before_snapshot


def test_signup_rejects_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "someone@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant_and_preserves_other_activities(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    before_count = len(app_module.activities[activity_name]["participants"])
    other_activity_before = list(app_module.activities["Gym Class"]["participants"])

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in app_module.activities[activity_name]["participants"]
    assert len(app_module.activities[activity_name]["participants"]) == before_count - 1
    assert app_module.activities["Gym Class"]["participants"] == other_activity_before


def test_unregister_rejects_non_enrolled_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "notenrolled@mergington.edu"
    before_snapshot = list(app_module.activities[activity_name]["participants"])

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
    assert app_module.activities[activity_name]["participants"] == before_snapshot


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "someone@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
