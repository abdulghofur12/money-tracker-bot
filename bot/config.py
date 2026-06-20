import os
from pathlib import Path
from dotenv import load_dotenv

BOT_DIR = Path(__file__).parent
load_dotenv(BOT_DIR / ".env")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")

GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "")
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON", "")
if GOOGLE_CREDENTIALS_FILE and not os.path.isabs(GOOGLE_CREDENTIALS_FILE):
    GOOGLE_CREDENTIALS_FILE = str(BOT_DIR / GOOGLE_CREDENTIALS_FILE)

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "YOUR_SPREADSHEET_ID")

print(f"DEBUG ENV - BOT_TOKEN set: {TELEGRAM_BOT_TOKEN != 'YOUR_TELEGRAM_BOT_TOKEN'}")
print(f"DEBUG ENV - SPREADSHEET_ID set: {SPREADSHEET_ID != 'YOUR_SPREADSHEET_ID'}")
print(f"DEBUG ENV - CREDENTIALS_JSON set: {bool(GOOGLE_CREDENTIALS_JSON)}")
print(f"DEBUG ENV - CREDENTIALS_FILE: {GOOGLE_CREDENTIALS_FILE}")
print(f"DEBUG ENV - All env keys with GOOGLE/SPREAD/TELEGRAM: {[k for k in os.environ if any(x in k.upper() for x in ['GOOGLE','SPREAD','TELEGRAM'])]}")

CATEGORIES = {
    "pengeluaran": {
        "🍜": "Makanan & Minuman",
        "🛒": "Belanja Kebutuhan",
        "🏠": "Sewa & Tempat Tinggal",
        "🚗": "Transportasi",
        "💊": "Kesehatan",
        "📚": "Pendidikan",
        "🎮": "Hiburan",
        "👗": "Pakaian",
        "📱": "Pulsa & Internet",
        "💰": "Tabungan",
        "🔧": "Perawatan",
        "📦": "Lainnya",
    },
    "pemasukan": {
        "💼": "Gaji",
        "📈": "Investasi",
        "🎁": "Bonus/Hadiah",
        "💼": "Freelance",
        "💵": "Pinjaman Masuk",
        "📦": "Lainnya",
    }
}

CATEGORY_ICONS = {
    "Makanan & Minuman": "🍜",
    "Belanja Kebutuhan": "🛒",
    "Sewa & Tempat Tinggal": "🏠",
    "Transportasi": "🚗",
    "Kesehatan": "💊",
    "Pendidikan": "📚",
    "Hiburan": "🎮",
    "Pakaian": "👗",
    "Pulsa & Internet": "📱",
    "Tabungan": "💰",
    "Perawatan": "🔧",
    "Gaji": "💼",
    "Investasi": "📈",
    "Bonus/Hadiah": "🎁",
    "Freelance": "💼",
    "Pinjaman Masuk": "💵",
    "Lainnya": "📦",
}

ICONS_BY_TYPE = {
    "pengeluaran": "💸",
    "pemasukan": "💰",
}
