"""
Test script for DistroFlow API server
Verifies all endpoints are working correctly
"""

import asyncio
import requests
import json
from datetime import datetime


API_URL = "http://127.0.0.1:8000"


def test_server_status():
    """Test GET / endpoint"""
    print("🧪 Testing server status...")
    try:
        response = requests.get(f"{API_URL}/")
        data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert data["status"] == "ok", "Server status not OK"
        assert "version" in data, "Version missing"
        assert "authenticated_platforms" in data, "Platforms missing"

        print(f"   ✅ Server status: {data['status']}")
        print(f"   ✅ Version: {data['version']}")
        print(f"   ✅ Authenticated platforms: {data['authenticated_platforms']}")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def test_platforms_list():
    """Test GET /platforms endpoint"""
    print("\n🧪 Testing platforms list...")
    try:
        response = requests.get(f"{API_URL}/platforms")
        data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert data["success"] is True, "Success not true"
        assert "platforms" in data, "Platforms list missing"

        print(f"   ✅ Found {len(data['platforms'])} platforms")
        for platform in data["platforms"]:
            status = "✅ Authenticated" if platform["authenticated"] else "❌ Not authenticated"
            print(f"      {platform['name']}: {status}")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def test_post_dry_run():
    """Test POST /post endpoint (will fail if no platforms authenticated, but tests the endpoint)"""
    print("\n🧪 Testing post endpoint (dry run)...")
    try:
        response = requests.post(
            f"{API_URL}/post",
            json={
                "platforms": ["twitter"],  # Will fail if not authenticated
                "content": "Test post from API test script",
                "title": None,
                "url": None,
            },
        )
        data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "results" in data, "Results missing"
        assert "timestamp" in data, "Timestamp missing"

        print(f"   ✅ Post endpoint working")
        print(f"   📝 Results: {len(data['results'])} platforms attempted")

        for result in data["results"]:
            if result["success"]:
                print(f"      ✅ {result['platform']}: Success")
            else:
                print(f"      ⚠️  {result['platform']}: {result['error']}")

        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def test_api_docs():
    """Test that API docs are accessible"""
    print("\n🧪 Testing API documentation...")
    try:
        response = requests.get(f"{API_URL}/docs")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "swagger" in response.text.lower() or "openapi" in response.text.lower(), \
            "Doesn't look like API docs"

        print(f"   ✅ API docs accessible at {API_URL}/docs")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("DistroFlow API Server Tests")
    print("=" * 60)
    print(f"\nTesting server at: {API_URL}")
    print(f"Time: {datetime.now().isoformat()}\n")

    results = {
        "Server Status": test_server_status(),
        "Platforms List": test_platforms_list(),
        "Post Endpoint": test_post_dry_run(),
        "API Documentation": test_api_docs(),
    }

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20s} {status}")

    print("\n" + "-" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)

    if passed == total:
        print("\n🎉 All tests passed! Server is working correctly.")
        print("\n💡 Next steps:")
        print("   1. Load extension in Chrome (chrome://extensions/)")
        print("   2. Click extension icon to test UI")
        print("   3. Try posting to authenticated platforms")
    else:
        print("\n⚠️  Some tests failed.")
        print("\n💡 Troubleshooting:")
        print("   1. Make sure server is running: distroflow serve")
        print("   2. Check server logs in terminal")
        print("   3. Verify dependencies installed: pip install fastapi uvicorn")

    return passed == total


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        exit(1)
