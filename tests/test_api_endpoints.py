"""Tests for API endpoints."""

import pytest


class TestRootEndpoint:
    """Test the root endpoint."""

    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]


class TestGetActivitiesEndpoint:
    """Test the /activities endpoint."""

    def test_get_activities_returns_dict(self, client, reset_activities):
        """Test that GET /activities returns all activities as a dictionary."""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_get_activities_contains_required_fields(self, client, reset_activities):
        """Test that each activity has required fields."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)

    def test_get_activities_includes_chess_club(self, client, reset_activities):
        """Test that Chess Club is in the activities list."""
        response = client.get("/activities")
        data = response.json()
        assert "Chess Club" in data

    def test_get_activities_includes_programming_class(self, client, reset_activities):
        """Test that Programming Class is in the activities list."""
        response = client.get("/activities")
        data = response.json()
        assert "Programming Class" in data


class TestSignupForActivityEndpoint:
    """Test the /activities/{activity_name}/signup endpoint."""

    def test_signup_new_participant(self, client, reset_activities):
        """Test signing up a new participant for an activity."""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_adds_participant_to_list(self, client, reset_activities):
        """Test that signup actually adds the participant to the activity."""
        email = "newstudent@mergington.edu"
        client.post(f"/activities/Chess Club/signup?email={email}")
        
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Chess Club"]["participants"]

    def test_signup_duplicate_fails(self, client, reset_activities):
        """Test that signing up an already registered student fails."""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        """Test that signing up for a non-existent activity fails."""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_multiple_different_activities(self, client, reset_activities):
        """Test that a student can sign up for multiple activities."""
        email = "multiactivity@mergington.edu"
        
        # Sign up for Chess Club
        response1 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response1.status_code == 200
        
        # Sign up for Programming Class
        response2 = client.post(f"/activities/Programming Class/signup?email={email}")
        assert response2.status_code == 200
        
        # Verify both signups
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]

    def test_signup_response_message_format(self, client, reset_activities):
        """Test that signup response message is properly formatted."""
        email = "test@mergington.edu"
        response = client.post(f"/activities/Drama Club/signup?email={email}")
        data = response.json()
        assert data["message"] == f"Signed up {email} for Drama Club"


class TestUnregisterFromActivityEndpoint:
    """Test the /activities/{activity_name}/unregister endpoint."""

    def test_unregister_existing_participant(self, client, reset_activities):
        """Test unregistering an existing participant."""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.post(f"/activities/Chess Club/unregister?email={email}")
        assert response.status_code == 200
        data = response.json()
        assert "Removed" in data["message"]

    def test_unregister_removes_participant_from_list(self, client, reset_activities):
        """Test that unregister actually removes the participant."""
        email = "michael@mergington.edu"
        client.post(f"/activities/Chess Club/unregister?email={email}")
        
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities["Chess Club"]["participants"]

    def test_unregister_nonexistent_participant_fails(self, client, reset_activities):
        """Test that unregistering a non-existent participant fails."""
        response = client.post(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]

    def test_unregister_nonexistent_activity_fails(self, client, reset_activities):
        """Test that unregistering from a non-existent activity fails."""
        response = client.post(
            "/activities/Nonexistent Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_response_message_format(self, client, reset_activities):
        """Test that unregister response message is properly formatted."""
        email = "michael@mergington.edu"
        response = client.post(f"/activities/Chess Club/unregister?email={email}")
        data = response.json()
        assert data["message"] == f"Removed {email} from Chess Club"

    def test_signup_after_unregister(self, client, reset_activities):
        """Test that a student can re-sign up after unregistering."""
        email = "michael@mergington.edu"
        
        # Unregister
        client.post(f"/activities/Chess Club/unregister?email={email}")
        
        # Re-register
        response = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response.status_code == 200
        
        # Verify re-registration
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Chess Club"]["participants"]
