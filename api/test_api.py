"""
Example API requests for testing.
Run these examples to test the API functionality.

Prerequisites:
1. Database running: docker-compose up -d
2. API running: python app.py
"""

import requests
import json

# Configuration
API_BASE_URL = "http://localhost:5000"
headers = {"Content-Type": "application/json"}

# Store tokens and IDs for subsequent requests
access_token = None
media_id = None
rating_id = None


def print_response(response, title):
    """Print formatted response."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_health_check():
    """Test health check endpoint."""
    response = requests.get(f"{API_BASE_URL}/health")
    print_response(response, "1. Health Check")
    return response.status_code == 200


def test_register():
    """Test user registration."""
    global access_token
    
    data = {
        "username": "test_user_api",
        "email": "testapi@example.com",
        "password": "password123"
    }
    
    response = requests.post(
        f"{API_BASE_URL}/api/auth/register",
        headers=headers,
        json=data
    )
    
    print_response(response, "2. User Registration")
    
    if response.status_code == 201:
        access_token = response.json().get("access_token")
        return True
    return False


def test_login():
    """Test user login."""
    global access_token
    
    data = {
        "username": "test_user_api",
        "password": "password123"
    }
    
    response = requests.post(
        f"{API_BASE_URL}/api/auth/login",
        headers=headers,
        json=data
    )
    
    print_response(response, "3. User Login")
    
    if response.status_code == 200:
        access_token = response.json().get("access_token")
        return True
    return False


def test_get_current_user():
    """Test getting current user."""
    auth_headers = {**headers, "Authorization": f"Bearer {access_token}"}
    
    response = requests.get(
        f"{API_BASE_URL}/api/auth/me",
        headers=auth_headers
    )
    
    print_response(response, "4. Get Current User")
    return response.status_code == 200


def test_create_content():
    """Test creating media content."""
    global media_id
    
    auth_headers = {**headers, "Authorization": f"Bearer {access_token}"}
    
    data = {
        "title": "API Test Game",
        "description": "A game created via API for testing",
        "category": "game",
        "thumbnail_url": "https://example.com/test-thumb.jpg",
        "content_url": "https://example.com/test-game.zip"
    }
    
    response = requests.post(
        f"{API_BASE_URL}/api/content",
        headers=auth_headers,
        json=data
    )
    
    print_response(response, "5. Create Media Content")
    
    if response.status_code == 201:
        media_id = response.json().get("content", {}).get("media_id")
        return True
    return False


def test_list_content():
    """Test listing all content."""
    params = {
        "page": 1,
        "per_page": 5,
        "category": "game"
    }
    
    response = requests.get(
        f"{API_BASE_URL}/api/content",
        params=params
    )
    
    print_response(response, "6. List Media Content (Filtered)")
    return response.status_code == 200


def test_get_content():
    """Test getting specific content."""
    response = requests.get(f"{API_BASE_URL}/api/content/{media_id}")
    print_response(response, "7. Get Specific Content")
    return response.status_code == 200


def test_update_content():
    """Test updating content."""
    auth_headers = {**headers, "Authorization": f"Bearer {access_token}"}
    
    data = {
        "title": "API Test Game - Updated",
        "description": "Updated description"
    }
    
    response = requests.put(
        f"{API_BASE_URL}/api/content/{media_id}",
        headers=auth_headers,
        json=data
    )
    
    print_response(response, "8. Update Content")
    return response.status_code == 200


def test_create_rating():
    """Test creating a rating."""
    global rating_id
    
    auth_headers = {**headers, "Authorization": f"Bearer {access_token}"}
    
    data = {
        "media_id": media_id,
        "score": 5,
        "comment": "Excellent test game!"
    }
    
    response = requests.post(
        f"{API_BASE_URL}/api/ratings",
        headers=auth_headers,
        json=data
    )
    
    print_response(response, "9. Create Rating")
    
    if response.status_code == 201:
        rating_id = response.json().get("rating", {}).get("rating_id")
        return True
    return False


def test_get_rating_stats():
    """Test getting rating statistics."""
    response = requests.get(
        f"{API_BASE_URL}/api/ratings/media/{media_id}/stats"
    )
    
    print_response(response, "10. Get Rating Statistics")
    return response.status_code == 200


def test_list_ratings():
    """Test listing ratings."""
    params = {"media_id": media_id}
    
    response = requests.get(
        f"{API_BASE_URL}/api/ratings",
        params=params
    )
    
    print_response(response, "11. List Ratings")
    return response.status_code == 200


def test_update_rating():
    """Test updating a rating."""
    auth_headers = {**headers, "Authorization": f"Bearer {access_token}"}
    
    data = {
        "score": 4,
        "comment": "Updated comment - still great!"
    }
    
    response = requests.put(
        f"{API_BASE_URL}/api/ratings/{rating_id}",
        headers=auth_headers,
        json=data
    )
    
    print_response(response, "12. Update Rating")
    return response.status_code == 200


def cleanup():
    """Clean up test data (optional)."""
    auth_headers = {**headers, "Authorization": f"Bearer {access_token}"}
    
    # Delete rating
    if rating_id:
        response = requests.delete(
            f"{API_BASE_URL}/api/ratings/{rating_id}",
            headers=auth_headers
        )
        print_response(response, "13. Delete Rating (Cleanup)")
    
    # Delete content
    if media_id:
        response = requests.delete(
            f"{API_BASE_URL}/api/content/{media_id}",
            headers=auth_headers
        )
        print_response(response, "14. Delete Content (Cleanup)")


def run_all_tests():
    """Run all test examples."""
    print("\n" + "="*60)
    print("CONTENT SHARING PLATFORM API - TEST EXAMPLES")
    print("="*60)
    
    tests = [
        ("Health Check", test_health_check),
        ("Register User", test_register),
        ("Login User", test_login),
        ("Get Current User", test_get_current_user),
        ("Create Content", test_create_content),
        ("List Content", test_list_content),
        ("Get Content", test_get_content),
        ("Update Content", test_update_content),
        ("Create Rating", test_create_rating),
        ("Get Rating Stats", test_get_rating_stats),
        ("List Ratings", test_list_ratings),
        ("Update Rating", test_update_rating),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, "✓ PASSED" if result else "✗ FAILED"))
        except Exception as e:
            results.append((name, f"✗ ERROR: {str(e)}"))
    
    # Cleanup
    print("\n" + "="*60)
    print("CLEANUP")
    print("="*60)
    try:
        cleanup()
    except Exception as e:
        print(f"Cleanup error: {e}")
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for name, result in results:
        print(f"{name:.<40} {result}")
    
    passed = sum(1 for _, r in results if "PASSED" in r)
    total = len(results)
    print(f"\n{passed}/{total} tests passed")


if __name__ == "__main__":
    run_all_tests()
