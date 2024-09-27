#!/usr/bin/env python

import requests

# Define Superset URL and login credentials
SUP_URL = "http://localhost:8088"
USERNAME = "admin"
PASSWORD = "ilg007"

# Authentication request to get a JWT token
auth_url = f"{SUP_URL}/api/v1/security/login"
headers = {
    "Content-Type": "application/json",
}

payload = {
    "username": USERNAME,
    "password": PASSWORD,
    "provider": "db",
    "refresh": True,
}

# Post request for token
response = requests.post(auth_url, json=payload, headers=headers)
if response.status_code == 200:
    auth_token = response.json()['access_token']
    print(auth_token)
    print("Authentication Successful, Token Retrieved!")
else:
    print(f"Authentication failed: {response.content}")

