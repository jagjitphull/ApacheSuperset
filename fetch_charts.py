#!/usr/bin/env python

import requests

# Superset instance details
SUP_URL = "http://localhost:8088"  # Replace with your Superset URL
USERNAME = "admin"         # Replace with your Superset username
PASSWORD = "ilg007"         # Replace with your Superset password

# 1. Authenticate and get the Bearer token (auth_token)
auth_url = f"{SUP_URL}/api/v1/security/login"
auth_headers = {
    "Content-Type": "application/json",
}

# Payload for login credentials
auth_payload = {
    "username": USERNAME,
    "password": PASSWORD,
    "provider": "db",  # Change this if using a different provider like LDAP or OAuth
    "refresh": True
}

# Post request to authenticate and retrieve the Bearer token
response = requests.post(auth_url, json=auth_payload, headers=auth_headers)

# Check if the authentication was successful
if response.status_code == 200:
    # Extract the Bearer token from the response
    auth_token = response.json().get("access_token")
    print(f"Authentication successful! Access Token: {auth_token}")

    # 2. Use the token to fetch the list of charts
    charts_url = f"{SUP_URL}/api/v1/chart/"

    # Set up the headers with the Bearer token
    headers_with_token = {
        "Authorization": f"Bearer {auth_token}",  # Use the Bearer token here
        "Content-Type": "application/json",
    }

    # GET request to fetch charts
    chart_response = requests.get(charts_url, headers=headers_with_token)

    # Check if the request was successful
    if chart_response.status_code == 200:
        charts = chart_response.json()
        print("Charts fetched successfully!")
        # Print the charts
        for chart in charts['result']:
            print(f"Chart ID: {chart['id']}, Chart Name: {chart['slice_name']}")
    else:
        print(f"Failed to fetch charts: {chart_response.content}")
else:
    print(f"Authentication failed: {response.content}")

