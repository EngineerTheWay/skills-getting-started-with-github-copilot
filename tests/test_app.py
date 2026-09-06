import pytest

from src.app import activities


def test_root_redirects_to_static_index(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_data(client):
    # Arrange
    expected_activity = activities["Chess Club"]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()["Chess Club"] == expected_activity


def test_signup_normalizes_username_and_updates_activity(client):
    # Arrange
    activity_name = "Soccer Club"
    username = "  Ada  "

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"username": username},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up ada@mergington.edu for Soccer Club"
    }
    assert "ada@mergington.edu" in activities[activity_name]["participants"]


def test_signup_is_visible_in_activity_response(client):
    # Arrange
    activity_name = "Art Club"
    username = "maya"
    client.post(
        f"/activities/{activity_name}/signup",
        params={"username": username},
    )

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert "maya@mergington.edu" in response.json()[activity_name]["participants"]


def test_duplicate_signup_is_rejected_after_normalization(client):
    # Arrange
    activity_name = "Drama Club"
    client.post(
        f"/activities/{activity_name}/signup",
        params={"username": "Alice"},
    )

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"username": " alice "},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_unknown_activity_returns_not_found(client):
    # Arrange
    activity_name = "Unknown Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"username": "student"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


@pytest.mark.parametrize("username", ["", "   ", "student@example.com"])
def test_invalid_username_returns_bad_request(client, username):
    # Arrange
    activity_name = "Debate Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"username": username},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Enter a valid username without an email domain"


def test_missing_username_returns_validation_error(client):
    # Arrange
    activity_name = "Science Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup")

    # Assert
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "username"]


def test_activity_name_with_spaces_can_be_used_for_signup(client):
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"username": "student"},
    )

    # Assert
    assert response.status_code == 200
    assert "student@mergington.edu" in activities[activity_name]["participants"]
