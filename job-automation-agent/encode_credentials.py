import base64
import os

CREDENTIALS_FILE = "credentials.json"
OUTPUT_FILE = "credentials_base64.txt"

if not os.path.exists(CREDENTIALS_FILE):
    print(f"Error: {CREDENTIALS_FILE} not found.")
else:
    with open(CREDENTIALS_FILE, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    with open(OUTPUT_FILE, "w") as f:
        f.write(encoded)

    print(f"Success! Encoded credentials written to {OUTPUT_FILE}")
