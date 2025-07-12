#!/usr/bin/env python3

import requests
import json

# Configuration
base_url = "http://localhost:3001"
api_token = "156153F-4J1MSJ2-PZE4NHP-12R60AH"

# Workspaces endpoint
workspaces_url = f"{base_url}/api/v1/workspaces"

headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {api_token}"
}

try:
    response = requests.get(workspaces_url, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        workspaces = response.json()
        print(f"Workspaces: {json.dumps(workspaces, indent=2)}")
        
        # Extract workspace names/slugs for easy reference
        if isinstance(workspaces, dict) and 'workspaces' in workspaces:
            print("\nAvailable workspace slugs:")
            for workspace in workspaces['workspaces']:
                print(f"- {workspace.get('slug', 'N/A')}")
    else:
        print(f"Error: {response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")