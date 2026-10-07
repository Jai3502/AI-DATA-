import json
import urllib.request
import urllib.error

from app.core.security import create_access_token

USER_ID = "94aa0fba-716d-409a-92e0-e52b9b31fb63"
DATASET_ID = "8423f2cd-1de2-4293-b39c-5c585fbbd60b"

token = create_access_token(USER_ID)

url = f"http://127.0.0.1:8000/datasets/{DATASET_ID}/forecast"

data = json.dumps({
    "horizon": 12
}).encode()

request = urllib.request.Request(
    url,
    data=data,
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    },
    method="POST",
)

print("Testing user: test2@example.com")
print("Sending request...")

try:
    response = urllib.request.urlopen(request)

    print("STATUS:", response.status)
    print("RESPONSE:")
    print(response.read().decode())

except urllib.error.HTTPError as error:
    print("STATUS:", error.code)
    print("RESPONSE:")
    print(error.read().decode())