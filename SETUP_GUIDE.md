a# 💰 Money Tracker - Setup Guide

Sistem pencatat pengeluaran/pemasukan via Telegram Bot dengan dashboard web.

## 📋 Fitur

- **Telegram Bot**: Catat transaksi langsung dari Telegram
- **Google Sheets**: Database otomatis terupdate
- **Web Dashboard**: Visualisasi data dengan chart menarik
- **Real-time Sync**: Dashboard otomatis sync dengan Google Sheets
- **Auto-refresh**: Data terupdate setiap 30 detik
- **Kategori Otomatis**: 18 kategori dengan icon menarik

## 🚀 Setup

### 1. Buat Google Service Account

1. Buka [Google Cloud Console](https://console.cloud.google.com/)
2. Buat project baru
3. Enable APIs: Google Sheets API & Google Drive API
4. Buat Service Account:
   - IAM & Admin → Service Accounts → Create
   - Berikan nama (contoh: `money-tracker`)
   - Buat key (JSON) dan download
5. Rename file JSON menjadi `credentials.json` dan letakkan di folder `bot/`

### 2. Buat Google Spreadsheet

1. Buat spreadsheet baru di [Google Sheets](https://sheets.google.com/)
2. Rename sheet pertama menjadi "Transaksi"
3. Tambah sheet baru bernama "Ringkasan"
4. Copy Spreadsheet ID dari URL:
   ```
   https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/edit
   ```
5. Share spreadsheet dengan email Service Account:
   - Klik Share → Tambah email service account
   - Berikan akses Editor

### 3. Buat Telegram Bot

1. Buka Telegram, cari `@BotFather`
2. Kirim `/newbot`
3. Berikan nama bot (contoh: `Money Tracker Bot`)
4. Berikan username (contoh: `my_money_tracker_bot`)
5. Copy token yang diberikan

### 4. Setup Environment Variables

Buat file `.env` di folder `bot/`:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
GOOGLE_CREDENTIALS_FILE=credentials.json
SPREADSHEET_ID=your_spreadsheet_id_here
```

### 5. Install Dependencies

```bash
cd bot
pip install -r requirements.txt
```

### 6. Jalankan Bot

```bash
python bot.py
```

### 7. Export Data untuk Web Dashboard

```bash
cd web
python export_data.py
```

### 8. Jalankan Web Dashboard (Dengan Sync)

```bash
cd web
pip install python-dotenv
python server.py
```

Buka browser: `http://localhost:8000`

**Fitur Sync:**
- Data auto-refresh setiap 30 detik
- Klik tombol 🔄 Refresh untuk manual refresh
- Indikator status sinkronisasi di pojok kanan atas

### 9. Export Data Manual (Optional)

Jika ingin export data ke file JSON tanpa server:

```bash
cd web
python export_data.py
```

## 📱 Cara Menggunakan Bot

### Menu Utama
Kirim `/start` untuk membuka menu utama.

### Catat Pengeluaran
1. Klik "💸 Pengeluaran"
2. Pilih kategori
3. Masukkan jumlah
4. (Opsional) Masukkan keterangan

### Catat Pemasukan
1. Klik "💰 Pemasukan"
2. Pilih kategori
3. Masukkan jumlah
4. (Opsional) Masukkan keterangan

### Lihat Ringkasan
Klik "📊 Ringkasan" atau kirim `/summary`

### Lihat Riwayat
Klik "📋 Riwayat" atau kirim `/history`

## 🏷️ Kategori yang Tersedia

### Pengeluaran
| Icon | Kategori |
|------|----------|
| 🍜 | Makanan & Minuman |
| 🛒 | Belanja Kebutuhan |
| 🏠 | Sewa & Tempat Tinggal |
| 🚗 | Transportasi |
| 💊 | Kesehatan |
| 📚 | Pendidikan |
| 🎮 | Hiburan |
| 👗 | Pakaian |
| 📱 | Pulsa & Internet |
| 💰 | Tabungan |
| 🔧 | Perawatan |
| 📦 | Lainnya |

### Pemasukan
| Icon | Kategori |
|------|----------|
| 💼 | Gaji |
| 📈 | Investasi |
| 🎁 | Bonus/Hadiah |
| 💼 | Freelance |
| 💵 | Pinjaman Masuk |
| 📦 | Lainnya |

## 📁 Struktur Folder

```
money-tracker/
├── bot/
│   ├── bot.py              # Telegram bot
│   ├── config.py           # Konfigurasi
│   ├── sheets.py           # Google Sheets integration
│   ├── requirements.txt    # Dependencies
│   ├── credentials.json    # Google Service Account key
│   └── .env                # Environment variables
├── web/
│   ├── index.html          # Dashboard HTML
│   ├── style.css           # Styles
│   ├── app.js              # JavaScript
│   ├── export_data.py      # Export data ke JSON
│   └── data.json           # Data untuk dashboard
└── README.md
```

## 🔧 Troubleshooting

### Bot tidak menyapa
- Pastikan token bot benar di `.env`
- Cek koneksi internet

### Data tidak masuk ke Google Sheets
- Pastikan Service Account sudah di-share ke spreadsheet
- Cek nama sheet harus "Transaksi"

### Dashboard tidak menampilkan data
- Jalankan `export_data.py` terlebih dahulu
- Pastikan `data.json` ada di folder `web/`

## 📝 Contoh Transaksi

```
Pengeluaran:
🍜 Makanan & Minuman → 25000 → Makan siang
🚗 Transportasi → 50000 → Grab ke kantor
📱 Pulsa & Internet → 100000 → Paket data

Pemasukan:
💼 Gaji → 5000000
💼 Freelance → 1000000 → Proyek website
```
