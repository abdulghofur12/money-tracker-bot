import gspread
from google.oauth2.service_account import Credentials
import json
import os
from datetime import datetime

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

def export_to_json(credentials_file, spreadsheet_id, output_file="data.json"):
    try:
        creds = Credentials.from_service_account_file(credentials_file, scopes=SCOPES)
        gc = gspread.authorize(creds)

        spreadsheet = gc.open_by_key(spreadsheet_id)
        sheet = spreadsheet.worksheet("Transaksi")

        all_values = sheet.get_all_values()

        if len(all_values) <= 1:
            transactions = []
        else:
            transactions = []
            for row in all_values[1:]:
                if len(row) >= 6:
                    transactions.append({
                        "id": row[0],
                        "date": row[1],
                        "time": row[2],
                        "type": row[3],
                        "category": row[4],
                        "amount": row[5],
                        "note": row[6] if len(row) > 6 else "",
                    })

        output = {
            "last_update": datetime.now().isoformat(),
            "transactions": transactions,
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"✅ Data exported to {output_file}")
        print(f"📊 Total transactions: {len(transactions)}")
        return True

    except Exception as e:
        print(f"❌ Error exporting data: {e}")
        return False


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    credentials_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    spreadsheet_id = os.getenv("SPREADSHEET_ID", "YOUR_SPREADSHEET_ID")

    export_to_json(credentials_file, spreadsheet_id)
