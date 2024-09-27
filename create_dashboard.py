#!/usr/bin/env python

import requests

# Superset instance details
SUP_URL = "http://localhost:8088"  # Replace with your Superset URL
USERNAME = "admin"         # Replace with your Superset username
PASSWORD = "ilg007"         # Replace with your Superset password

# Start a session to manage cookies and requests
session = requests.Session()

# 1. Authenticate and get the Bearer token (auth_token)
auth_url = f"{SUP_URL}/api/v1/security/login"
auth_headers = {
    "Content-Type": "application/json",
}

# Payload with login credentials
auth_payload = {
    "username": USERNAME,
    "password": PASSWORD,
    "provider": "db",  # Change this if you're using LDAP or OAuth
    "refresh": True
}

# Post request to authenticate and retrieve the Bearer token
response = session.post(auth_url, json=auth_payload, headers=auth_headers)

# Check if authentication was successful
if response.status_code == 200:
    # Extract the Bearer token from the response
    auth_token = response.json().get("access_token")
    print(f"Authentication successful! Access Token: {auth_token}")

    # 2. Get the CSRF token using the session
    csrf_url = f"{SUP_URL}/api/v1/security/csrf_token/"
    csrf_headers = {
        "Authorization": f"Bearer {auth_token}",  # Use the Bearer token
        "Content-Type": "application/json",
    }

    # Send GET request to retrieve the CSRF token (this request also handles the cookies)
    csrf_response = session.get(csrf_url, headers=csrf_headers)

    if csrf_response.status_code == 200:
        # Extract CSRF token from the response
        csrf_token = csrf_response.json().get("result")
        print(f"CSRF token retrieved: {csrf_token}")

        # 3. Use the tokens to create a new dashboard
        create_dashboard_url = f"{SUP_URL}/api/v1/dashboard/"

        # Set up the headers with the Bearer and CSRF token
        headers_with_token = {
            "Authorization": f"Bearer {auth_token}",  # Use the Bearer token here
            "Content-Type": "application/json",
            "X-CSRFToken": csrf_token,  # Include the CSRF token here
        }

        # Payload for creating a new dashboard
        dashboard_payload = {
            "dashboard_title": "JP Dashboard",  # Title of the dashboard
            "published": True,                     # Set to True to publish immediately
            "position_json": '{}',                 # Empty layout (can be customized)
            "json_metadata": '{}',                 # Custom metadata (optional)
        }

        # Post request to create the dashboard (using session to maintain cookies)
        create_response = session.post(create_dashboard_url, json=dashboard_payload, headers=headers_with_token)

        # Check if the request was successful
        if create_response.status_code == 201:
            dashboard = create_response.json()
            print("Dashboard created successfully!")
            print(f"Dashboard ID: {dashboard['id']}, Dashboard Title: {dashboard['dashboard_title']}")
        else:
            print(f"Failed to create dashboard: {create_response.content}")
    else:
        print(f"Failed to retrieve CSRF token: {csrf_response.content}")
else:
    print(f"Authentication failed: {response.content}")

