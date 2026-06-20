import base64
import sys
import os

def main():
    cred_file = os.path.join(os.path.dirname(__file__), "credentials.json")
    if not os.path.exists(cred_file):
        print("credentials.json not found!")
        sys.exit(1)

    with open(cred_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    print("\nCopy this value and paste it as GOOGLE_CREDENTIALS_JSON in Railway:\n")
    print(encoded)

if __name__ == "__main__":
    main()
