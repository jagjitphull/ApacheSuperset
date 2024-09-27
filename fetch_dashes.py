#!/usr/bin/env python


import requests

# Superset URL and credentials
SUP_URL = "http://localhost:8088"
USERNAME = "admin"
PASSWORD = "ilg007"

# 1. Authenticate and get the Bearer token (auth_token)
auth_url = f"{SUP_URL}/api/v1/security/login"
auth_headers = {
    "Content-Type": "application/json",
}

# Payload with login credentials
auth_payload = {
    "username": USERNAME,
    "password": PASSWORD,
    "provider": "db",  # or use the right auth provider like "ldap" or "oauth"
    "refresh": True
}

# Post request to authenticate and retrieve the token
response = requests.post(auth_url, json=auth_payload, headers=auth_headers)

# Check if authentication was successful
if response.status_code == 200:
    # Extract the Bearer token from the response
    auth_token = response.json().get("access_token")
    print(f"Authentication successful! Access Token: {auth_token}")

    # 2. Use the token to make authorized requests
    # Example: Fetch the list of dashboards
    dashboards_url = f"{SUP_URL}/api/v1/dashboard/"

    # Assign the Bearer token in the request headers
    headers_with_token = {
        "Authorization": f"Bearer {auth_token}",  # Bearer token added here
        "Content-Type": "application/json",
    }

    # Get request to fetch dashboards
    dashboard_response = requests.get(dashboards_url, headers=headers_with_token)

    if dashboard_response.status_code == 200:
        # Successfully retrieved dashboards
        dashboards = dashboard_response.json()
        print("Dashboards:", dashboards)
    else:
        print(f"Failed to fetch dashboards: {dashboard_response.content}")
else:
    print(f"Authentication failed: {response.content}")

