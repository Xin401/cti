import requests
import os

EXCEL_LOGIC_APP_WEBHOOK_URL = os.environ.get("EXCEL_LOGIC_APP_WEBHOOK_URL")
EMAIL_LOGIC_APP_WEBHOOK_URL = os.environ.get("EMAIL_LOGIC_APP_WEBHOOK_URL")
def send_to_logic_app(data):
    try:
        headers = {'Content-Type': 'application/json'}
        print("Sending data to Logic App...")
        response = requests.post(EXCEL_LOGIC_APP_WEBHOOK_URL, headers=headers, json=data)
        response.raise_for_status()
    except Exception as e:
        print(f"Error sending data to Logic App: {e}")

def send_email(data):
    try:
        headers = {'Content-Type': 'application/json'}
        print("Sending data to Logic App...")
        response = requests.post(EMAIL_LOGIC_APP_WEBHOOK_URL, headers=headers, json=data)
        response.raise_for_status()
    except Exception as e:
        print(f"Error sending data to Logic App: {e}")