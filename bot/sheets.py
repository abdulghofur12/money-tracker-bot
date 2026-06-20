import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timezone, timedelta
import traceback
import os
import json
import tempfile
import base64
from config import GOOGLE_CREDENTIALS_FILE, GOOGLE_CREDENTIALS_JSON, SPREADSHEET_ID, CATEGORY_ICONS, CATEGORIES

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

WIB = timezone(timedelta(hours=7))

class SheetsManager:
    def __init__(self):
        self.gc = None
        self.spreadsheet = None
        self.sheet = None
        self.summary_sheet = None
        self.connected = False
        self.connect()

    def connect(self):
        try:
            creds_file = GOOGLE_CREDENTIALS_FILE
            creds_json = GOOGLE_CREDENTIALS_JSON

            if creds_json:
                creds_data = json.loads(base64.b64decode(creds_json).decode("utf-8"))
                creds_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False).name
                with open(creds_file, "w") as f:
                    json.dump(creds_data, f)
            else:
                print(f"Credentials: {GOOGLE_CREDENTIALS_FILE}")

            print(f"Spreadsheet ID: {SPREADSHEET_ID}")

            if not creds_file and not creds_json:
                raise ValueError("GOOGLE_CREDENTIALS_FILE or GOOGLE_CREDENTIALS_JSON not set")

            if not SPREADSHEET_ID or SPREADSHEET_ID == "YOUR_SPREADSHEET_ID":
                raise ValueError("SPREADSHEET_ID not set in .env")

            if not creds_json and not os.path.exists(creds_file):
                raise FileNotFoundError(f"Credentials file not found: {creds_file}")

            creds = Credentials.from_service_account_file(
                creds_file, scopes=SCOPES
            )
            self.gc = gspread.authorize(creds)
            self.spreadsheet = self.gc.open_by_key(SPREADSHEET_ID)

            try:
                self.sheet = self.spreadsheet.worksheet("Transaksi")
            except gspread.WorksheetNotFound:
                self.sheet = self.spreadsheet.add_worksheet(title="Transaksi", rows=1000, cols=10)
                self.sheet.update("A1:J1", [["ID", "Tanggal", "Waktu", "Tipe", "Kategori", "Jumlah", "Keterangan", "User", "Chat ID", "Icon"]])

            try:
                self.summary_sheet = self.spreadsheet.worksheet("Ringkasan")
            except gspread.WorksheetNotFound:
                self.summary_sheet = self.spreadsheet.add_worksheet(title="Ringkasan", rows=100, cols=10)
                self.summary_sheet.update("A1:E1", [["Kategori", "Total", "Jumlah Transaksi", "Tipe", "Persentase"]])

            self.connected = True
            print("Connected to Google Sheets!")
        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()
            self.connected = False
            raise

    def setup_sheets(self):
        if not self.connected:
            self.connect()

    def add_transaction(self, data):
        try:
            existing = self.sheet.get_all_values()
            next_row = len(existing) + 1 if existing else 2

            icon = CATEGORY_ICONS.get(data["category"], "📦")
            date_str = datetime.now(WIB).strftime("%Y-%m-%d")
            time_str = datetime.now(WIB).strftime("%H:%M:%S")

            row = [
                len(existing),
                date_str,
                time_str,
                data["type"],
                data["category"],
                data["amount"],
                data.get("note", ""),
                data.get("user", ""),
                data.get("chat_id", ""),
                icon
            ]

            self.sheet.update(f"A{next_row}:J{next_row}", [row])
            print(f"DEBUG: Written row {next_row}: {row}")

            try:
                if data["type"] == "pengeluaran":
                    self.sheet.format(f"A{next_row}:J{next_row}", {
                        "backgroundColor": {"red": 1, "green": 0.95, "blue": 0.95}
                    })
                else:
                    self.sheet.format(f"A{next_row}:J{next_row}", {
                        "backgroundColor": {"red": 0.95, "green": 1, "blue": 0.95}
                    })
            except Exception:
                pass

            verify = self.sheet.get_all_values()
            print(f"DEBUG: After write, sheet has {len(verify)} rows. Last row: {verify[-1] if verify else 'empty'}")

            self.update_summary()
            return True
        except Exception as e:
            print(f"Error adding transaction: {e}")
            traceback.print_exc()
            return False

    def get_transactions(self, limit=50):
        try:
            all_values = self.sheet.get_all_values()
            if len(all_values) <= 1:
                return []
            transactions = []
            for row in all_values[1:][-limit:]:
                transactions.append({
                    "id": row[0] if len(row) > 0 else "",
                    "date": row[1] if len(row) > 1 else "",
                    "time": row[2] if len(row) > 2 else "",
                    "type": row[3] if len(row) > 3 else "",
                    "category": row[4] if len(row) > 4 else "",
                    "amount": row[5] if len(row) > 5 else "0",
                    "note": row[6] if len(row) > 6 else "",
                    "user": row[7] if len(row) > 7 else "",
                    "chat_id": row[8] if len(row) > 8 else "",
                    "icon": row[9] if len(row) > 9 else ""
                })
            return list(reversed(transactions))
        except Exception as e:
            print(f"Error getting transactions: {e}")
            traceback.print_exc()
            return []

    def get_summary(self):
        try:
            transactions = self.sheet.get_all_values()
            print(f"DEBUG: get_summary - sheet has {len(transactions)} rows")
            if len(transactions) > 1:
                print(f"DEBUG: get_summary - sample row: {transactions[1]}")
            if len(transactions) <= 1:
                return {"total_income": 0, "total_expense": 0, "balance": 0, "categories": {}}

            total_income = 0
            total_expense = 0
            categories = {}

            for row in transactions[1:]:
                if len(row) >= 6:
                    tipe = row[3]
                    kategori = row[4]
                    try:
                        amount_str = row[5].replace("Rp", "").replace(".", "").replace(",", "").strip()
                        jumlah = float(amount_str)
                    except:
                        continue

                    if tipe == "pemasukan":
                        total_income += jumlah
                    elif tipe == "pengeluaran":
                        total_expense += jumlah

                    if kategori not in categories:
                        categories[kategori] = {"total": 0, "count": 0, "type": tipe}
                    categories[kategori]["total"] += jumlah
                    categories[kategori]["count"] += 1

            return {
                "total_income": total_income,
                "total_expense": total_expense,
                "balance": total_income - total_expense,
                "categories": categories
            }
        except Exception as e:
            print(f"Error getting summary: {e}")
            traceback.print_exc()
            return {"total_income": 0, "total_expense": 0, "balance": 0, "categories": {}}

    def update_summary(self):
        try:
            summary = self.get_summary()

            self.summary_sheet.clear()
            self.summary_sheet.update("A1:E1", [["Kategori", "Total", "Jumlah Transaksi", "Tipe", "Persentase"]])
            try:
                self.summary_sheet.format("A1:E1", {
                    "backgroundColor": {"red": 0.1, "green": 0.7, "blue": 0.4},
                    "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
                    "horizontalAlignment": "CENTER"
                })
            except Exception:
                pass

            row = 2
            total_all = summary["total_income"] + summary["total_expense"]
            for cat, data in summary["categories"].items():
                percentage = (data["total"] / total_all * 100) if total_all > 0 else 0
                icon = CATEGORY_ICONS.get(cat, "📦")
                self.summary_sheet.update(f"A{row}:E{row}", [[
                    f"{icon} {cat}",
                    f"Rp {data['total']:,.0f}",
                    data["count"],
                    data["type"],
                    f"{percentage:.1f}%"
                ]])
                row += 1

            self.summary_sheet.update(f"A{row}:E{row}", [["", "", "", "", ""]])
            row += 1
            self.summary_sheet.update(f"A{row}:E{row}", [["Total Pemasukan", f"Rp {summary['total_income']:,.0f}", "", "", ""]])
            row += 1
            self.summary_sheet.update(f"A{row}:E{row}", [["Total Pengeluaran", f"Rp {summary['total_expense']:,.0f}", "", "", ""]])
            row += 1
            self.summary_sheet.update(f"A{row}:E{row}", [["Saldo", f"Rp {summary['balance']:,.0f}", "", "", ""]])
        except Exception as e:
            print(f"Error updating summary: {e}")
            traceback.print_exc()

    def clear_all_data(self):
        try:
            self.sheet.clear()
            self.sheet.update("A1:J1", [["ID", "Tanggal", "Waktu", "Tipe", "Kategori", "Jumlah", "Keterangan", "User", "Chat ID", "Icon"]])
            try:
                self.sheet.format("A1:J1", {
                    "backgroundColor": {"red": 0.1, "green": 0.7, "blue": 0.4},
                    "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
                    "horizontalAlignment": "CENTER"
                })
            except Exception:
                pass
            self.summary_sheet.clear()
            self.summary_sheet.update("A1:E1", [["Kategori", "Total", "Jumlah Transaksi", "Tipe", "Persentase"]])
            return True
        except Exception as e:
            print(f"Error clearing data: {e}")
            traceback.print_exc()
            return False

    def delete_transaction(self, transaction_id):
        try:
            all_values = self.sheet.get_all_values()
            for i, row in enumerate(all_values[1:], start=2):
                if str(row[0]) == str(transaction_id):
                    print(f"DEBUG: Deleting row {i} with ID {transaction_id}")
                    self.sheet.delete_rows(i, i)
                    self.update_summary()
                    return True
            print(f"DEBUG: Transaction ID {transaction_id} not found. Rows: {[r[0] for r in all_values[1:]]}")
            return False
        except Exception as e:
            print(f"Error deleting transaction: {e}")
            traceback.print_exc()
            return False
