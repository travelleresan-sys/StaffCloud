#!/usr/bin/env python3
import requests
import sys

def test_route(url, description):
    try:
        response = requests.get(url, allow_redirects=False)
        print(f"✓ {description}: HTTP {response.status_code}")
        return True
    except Exception as e:
        print(f"✗ {description}: Error - {str(e)}")
        return False

def main():
    base_url = "http://127.0.0.1:5001"
    
    routes_to_test = [
        ("/", "TOP page"),
        ("/login", "Login page (redirected)"),
        ("/admin_login", "Admin login page"),
        ("/employee_login", "Employee login page"),
    ]
    
    print("Testing routes...")
    all_passed = True
    
    for route, description in routes_to_test:
        if not test_route(f"{base_url}{route}", description):
            all_passed = False
    
    if all_passed:
        print("\nAll basic routes are working!")
    else:
        print("\nSome routes have issues.")
        sys.exit(1)

if __name__ == "__main__":
    main()