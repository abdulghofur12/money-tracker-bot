import http.server
import socketserver
import json
import os
import sys
import traceback
from datetime import datetime
from urllib.parse import urlparse
from pathlib import Path

BOT_DIR = Path(__file__).parent.parent / "bot"
sys.path.insert(0, str(BOT_DIR))

from dotenv import load_dotenv
load_dotenv(BOT_DIR / ".env")

PORT = 8000
WEB_DIR = os.path.dirname(os.path.abspath(__file__))

sheets_manager = None
sheets_error = None

def get_sheets_manager():
    global sheets_manager, sheets_error
    if sheets_manager is None:
        try:
            from sheets import SheetsManager
            sheets_manager = SheetsManager()
            sheets_error = None
            print("[OK] Connected to Google Sheets")
        except Exception as e:
            sheets_error = str(e)
            print(f"[WARN] Could not connect to Google Sheets: {e}")
            sheets_manager = False
    return sheets_manager

class MoneyTrackerHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_GET(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path == "/api/data":
            self.send_api_response()
        elif parsed_path.path == "/api/refresh":
            self.refresh_data()
        elif parsed_path.path == "/api/status":
            self.send_status()
        else:
            super().do_GET()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def refresh_data(self):
        global sheets_manager, sheets_error
        sheets_manager = None
        sheets_error = None
        get_sheets_manager()
        self.send_api_response()

    def send_status(self):
        status = {
            "sheets_connected": sheets_manager is not None and sheets_manager is not False,
            "error": sheets_error,
            "credentials_file": os.getenv("GOOGLE_CREDENTIALS_FILE", ""),
            "spreadsheet_id": os.getenv("SPREADSHEET_ID", ""),
        }
        self.send_response(200)
        self.send_header("Content-type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(status, ensure_ascii=False).encode("utf-8"))

    def send_api_response(self):
        try:
            manager = get_sheets_manager()

            if manager and manager is not False:
                transactions = manager.get_transactions(limit=200)
                summary = manager.get_summary()

                data = {
                    "last_update": datetime.now().isoformat(),
                    "source": "google_sheets",
                    "transactions": transactions,
                    "summary": summary,
                }
            else:
                data = {
                    "last_update": datetime.now().isoformat(),
                    "source": "error",
                    "error": sheets_error or "Not connected",
                    "transactions": [],
                    "summary": {"total_income": 0, "total_expense": 0, "balance": 0, "categories": {}},
                }

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False, default=str).encode("utf-8"))

        except Exception as e:
            print(f"Error: {e}")
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            error = {"error": str(e), "source": "error"}
            self.wfile.write(json.dumps(error).encode("utf-8"))

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

def run_server():
    print("\n[CONFIG] Checking configuration...")
    print(f"[CONFIG] Bot dir: {BOT_DIR}")
    print(f"[CONFIG] Credentials: {os.getenv('GOOGLE_CREDENTIALS_FILE', 'NOT SET')}")
    print(f"[CONFIG] Spreadsheet ID: {os.getenv('SPREADSHEET_ID', 'NOT SET')}")

    get_sheets_manager()

    with socketserver.TCPServer(("", PORT), MoneyTrackerHandler) as httpd:
        print(f"\n[SERVER] Money Tracker Dashboard")
        print(f"[SERVER] Running at http://localhost:{PORT}")
        print(f"[TIPS] Auto-refresh: 30 seconds")
        print(f"[TIPS] Manual refresh: http://localhost:{PORT}/api/refresh")
        print(f"\nPress Ctrl+C to stop\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[SERVER] Stopped")

if __name__ == "__main__":
    run_server()
