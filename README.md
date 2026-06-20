# 💰 Money Tracker

Sistem pencatat pengeluaran/pemasukan via Telegram Bot dengan dashboard web dan Google Sheets.

## ✨ Fitur Utama

### 🤖 Telegram Bot
- Catat transaksi dengan mudah via chat
- 16 kategori dengan icon menarik
- Ringkasan keuangan instan
- Riwayat transaksi

### 📊 Google Sheets
- Database otomatis terupdate
- Sheet "Transaksi" untuk semua data
- Sheet "Ringkasan" untuk statistik
- Warna otomatis untuk tipe transaksi

### 🌐 Web Dashboard
- Tampilan modern dan responsif
- Chart visualisasi data
- Filter transaksi
- Ringkasan per kategori

## 🚀 Quick Start

1. **Clone/Create project**
2. **Setup Google Service Account** (lihat SETUP_GUIDE.md)
3. **Buat Google Spreadsheet**
4. **Buat Telegram Bot**
5. **Configure .env**
6. **Install & Run**

```bash
# Install dependencies
cd bot
pip install -r requirements.txt

# Run bot
python bot.py

# Export data for web
cd ../web
python export_data.py

# Run web server
python server.py
```

## 📱 Screenshots

### Telegram Bot
```
🏦 Selamat Datang di Money Tracker Bot!

Pilih menu di bawah ini:

💸 Pengeluaran    💰 Pemasukan
📊 Ringkasan      📋 Riwayat
❓ Bantuan
```

### Web Dashboard
- Summary cards dengan gradient warna
- Doughnut chart pengeluaran per kategori
- Line chart trend bulanan
- Tabel transaksi lengkap
- Grid kategori dengan icon

## 📁 Project Structure

```
money-tracker/
├── bot/                    # Telegram Bot
│   ├── bot.py             # Main bot logic
│   ├── config.py          # Configuration
│   ├── sheets.py          # Google Sheets integration
│   └── requirements.txt   # Python dependencies
├── web/                   # Web Dashboard
│   ├── index.html         # Dashboard page
│   ├── style.css          # Styles
│   ├── app.js             # Frontend logic
│   ├── server.py          # Simple HTTP server
│   └── export_data.py     # Data exporter
├── SETUP_GUIDE.md         # Detailed setup guide
└── README.md              # This file
```

## 🏷️ Kategori

### Pengeluaran (12)
🍜 Makanan | 🛒 Belanja | 🏠 Rumah | 🚗 Transport | 💊 Kesehatan | 📚 Pendidikan | 🎮 Hiburan | 👗 Pakaian | 📱 Pulsa | 💰 Tabungan | 🔧 Perawatan | 📦 Lainnya

### Pemasukan (6)
💼 Gaji | 📈 Investasi | 🎁 Bonus | 💼 Freelance | 💵 Pinjaman | 📦 Lainnya

## 🔧 Tech Stack

- **Backend**: Python, python-telegram-bot, gspread
- **Frontend**: HTML5, CSS3, JavaScript, Chart.js
- **Database**: Google Sheets API
- **Server**: Python HTTP Server

## 📝 License

MIT
