import requests
import json

# Disable SSL verification warnings
requests.packages.urllib3.disable_warnings()

# API endpoint
url = "https://localhost:8000/parse-ability"

# Test data
data = {
    "description": "When this card enters the battlefield, draw 2 cards."
}

# Make the request
response = requests.post(
    url,
    json=data,
    verify=False  # Skip SSL verification
)

# Print the response
print("Status Code:", response.status_code)
print("Response:")
print(json.dumps(response.json(), indent=2)) 