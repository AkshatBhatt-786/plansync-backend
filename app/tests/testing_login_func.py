import requests
import json

url = "http://localhost:5000/auth/accounts/login"
data = {
    "email": "akshatbhatt0786@gmail.com",
    "password": "Akshat@2005"
}

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

print(f"Sending POST to {url}")
print(f"Data: {json.dumps(data)}")

try:
    response = requests.post(url, json=data, headers=headers)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 201:
        print("\nSuccess! User Logged in.")
    elif response.status_code == 400:
        print("\nBad request. Check your data.")
    else:
        print(f"\nUnexpected response: {response.status_code}")
        
except Exception as e:
    print(f"\nError: {e}")