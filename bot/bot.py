import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from sheets import SheetsManager
from config import (
    TELEGRAM_BOT_TOKEN,
    CATEGORIES,
    CATEGORY_ICONS,
    ICONS_BY_TYPE,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

SELECTING_TYPE, SELECTING_CATEGORY, ENTERING_AMOUNT, ENTERING_NOTE = range(4)

sheets_manager = SheetsManager()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("💸 Pengeluaran", callback_data="type_pengeluaran"),
            InlineKeyboardButton("💰 Pemasukan", callback_data="type_pemasukan"),
        ],
        [
            InlineKeyboardButton("📊 Ringkasan", callback_data="summary"),
            InlineKeyboardButton("📋 Riwayat", callback_data="history"),
        ],
        [InlineKeyboardButton("❓ Bantuan", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        "🏦 *Selamat Datang di Money Tracker Bot!*\n\n"
        "Saya membantu Anda mencatat keuangan dengan mudah.\n\n"
        "Pilih menu di bawah ini:"
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("type_"):
        tipe = data.split("_")[1]
        context.user_data["type"] = tipe

        categories = CATEGORIES.get(tipe, {})
        keyboard = []
        row = []
        for icon, name in categories.items():
            row.append(InlineKeyboardButton(f"{icon} {name}", callback_data=f"cat_{name}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)

        keyboard.append([InlineKeyboardButton("🔙 Kembali", callback_data="back_to_start")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        tipe_label = "Pengeluaran" if tipe == "pengeluaran" else "Pemasukan"
        icon = ICONS_BY_TYPE.get(tipe, "📊")
        await query.edit_message_text(
            f"{icon} *{tipe_label}*\n\nPilih kategori:",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )
        return SELECTING_CATEGORY

    elif data.startswith("cat_"):
        category = data[4:]
        context.user_data["category"] = category
        await query.edit_message_text(
            f"📝 Masukkan jumlah {category}:\n\n"
            "Contoh: 50000 atau 50.000",
            parse_mode="Markdown",
        )
        return ENTERING_AMOUNT

    elif data == "summary":
        summary = sheets_manager.get_summary()
        text = format_summary(summary)
        keyboard = [[InlineKeyboardButton("🔙 Kembali", callback_data="back_to_start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    elif data == "history":
        transactions = sheets_manager.get_transactions(limit=10)
        text = format_history(transactions)
        keyboard = [[InlineKeyboardButton("🔙 Kembali", callback_data="back_to_start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    elif data == "help":
        text = (
            "❓ *Bantuan*\n\n"
            "Cara menggunakan bot ini:\n\n"
            "1️⃣ Pilih *Pengeluaran* atau *Pemasukan*\n"
            "2️⃣ Pilih *Kategori*\n"
            "3️⃣ Masukkan *Jumlah*\n"
            "4️⃣ (Opsional) Masukkan *Keterangan*\n\n"
            "*Contoh pencatatan:*\n"
            "• Pengeluaran → Makanan → 25000 → Makan siang\n"
            "• Pemasukan → Gaji → 5000000\n\n"
            "*Perintah:*\n"
            "/start - Menu utama\n"
            "/summary - Ringkasan keuangan\n"
            "/history - Riwayat transaksi\n"
            "/help - Bantuan"
        )
        keyboard = [[InlineKeyboardButton("🔙 Kembali", callback_data="back_to_start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    elif data == "back_to_start":
        keyboard = [
            [
                InlineKeyboardButton("💸 Pengeluaran", callback_data="type_pengeluaran"),
                InlineKeyboardButton("💰 Pemasukan", callback_data="type_pemasukan"),
            ],
            [
                InlineKeyboardButton("📊 Ringkasan", callback_data="summary"),
                InlineKeyboardButton("📋 Riwayat", callback_data="history"),
            ],
            [InlineKeyboardButton("❓ Bantuan", callback_data="help")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🏦 *Money Tracker Bot*\n\nPilih menu:",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )


async def amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace(".", "").replace(",", "")
    try:
        amount = float(text)
        context.user_data["amount"] = amount

        await update.message.reply_text(
            "📝 Masukkan keterangan (atau ketik /skip untuk skip):",
            parse_mode="Markdown",
        )
        return ENTERING_NOTE
    except ValueError:
        await update.message.reply_text(
            "❌ Jumlah tidak valid. Masukkan angka:\n\nContoh: 50000"
        )
        return ENTERING_AMOUNT


async def note_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    note = update.message.text if update.message.text != "/skip" else ""

    data = {
        "type": context.user_data.get("type", ""),
        "category": context.user_data.get("category", ""),
        "amount": context.user_data.get("amount", 0),
        "note": note,
        "user": update.message.from_user.first_name or "Unknown",
        "chat_id": str(update.message.chat_id),
    }

    success = sheets_manager.add_transaction(data)

    if success:
        icon = CATEGORY_ICONS.get(data["category"], "📦")
        tipe = "Pengeluaran" if data["type"] == "pengeluaran" else "Pemasukan"
        tipe_icon = ICONS_BY_TYPE.get(data["type"], "📊")

        text = (
            f"✅ *Transaksi Tercatat!*\n\n"
            f"{icon} *Kategori:* {data['category']}\n"
            f"{tipe_icon} *Tipe:* {tipe}\n"
            f"💵 *Jumlah:* Rp {data['amount']:,.0f}\n"
            f"📝 *Keterangan:* {data['note'] or '-'}\n"
            f"📅 *Tanggal:* {__import__('datetime').datetime.now().strftime('%d %B %Y %H:%M')}"
        )
    else:
        text = "❌ Gagal mencatat transaksi. Silakan coba lagi."

    keyboard = [
        [
            InlineKeyboardButton("💸 Catat Lagi", callback_data="type_pengeluaran"),
            InlineKeyboardButton("💰 Pemasukan", callback_data="type_pemasukan"),
        ],
        [InlineKeyboardButton("🏠 Menu Utama", callback_data="back_to_start")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Pencatatan dibatalkan.")
    return ConversationHandler.END


CLEAR_CONFIRM, CLEAR_CANCEL = range(4, 6)


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("✅ Ya, Hapus Semua", callback_data="clear_confirm"),
            InlineKeyboardButton("❌ Batal", callback_data="clear_cancel"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "⚠️ *Hapus Semua Data?*\n\n"
        "Semua transaksi di Google Sheet akan dihapus secara permanen.\n"
        "Data tidak bisa dikembalikan.\n\n"
        "Yakin ingin melanjutkan?",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )
    return CLEAR_CONFIRM


async def clear_confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "clear_confirm":
        success = sheets_manager.clear_all_data()
        if success:
            text = "🗑️ *Semua Data Berhasil Dihapus!*\n\nSheet sudah kosong dan siap digunakan untuk data baru."
        else:
            text = "❌ Gagal menghapus data. Silakan coba lagi."
    else:
        text = "❌ Penghapusan dibatalkan."

    keyboard = [[InlineKeyboardButton("🏠 Menu Utama", callback_data="back_to_start")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    context.user_data.clear()
    return ConversationHandler.END


async def summary_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    summary = sheets_manager.get_summary()
    text = format_summary(summary)
    await update.message.reply_text(text, parse_mode="Markdown")


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    transactions = sheets_manager.get_transactions(limit=10)
    text = format_history(transactions)
    await update.message.reply_text(text, parse_mode="Markdown")


def format_summary(summary):
    icon_income = ICONS_BY_TYPE["pemasukan"]
    icon_expense = ICONS_BY_TYPE["pengeluaran"]

    text = (
        f"📊 *Ringkasan Keuangan*\n\n"
        f"{icon_income} *Total Pemasukan:* Rp {summary['total_income']:,.0f}\n"
        f"{icon_expense} *Total Pengeluaran:* Rp {summary['total_expense']:,.0f}\n"
        f"💰 *Saldo:* Rp {summary['balance']:,.0f}\n\n"
    )

    if summary["categories"]:
        text += "*Detail per Kategori:*\n"
        for cat, data in summary["categories"].items():
            icon = CATEGORY_ICONS.get(cat, "📦")
            text += f"{icon} {cat}: Rp {data['total']:,.0f} ({data['count']}x)\n"

    return text


def format_history(transactions):
    if not transactions:
        return "📋 *Riwayat Transaksi*\n\nBelum ada transaksi."

    text = "📋 *Riwayat Transaksi (10 terakhir)*\n\n"

    for t in transactions[:10]:
        icon = t.get("icon", "📦")
        tipe_icon = "💸" if t["type"] == "pengeluaran" else "💰"
        amount_str = t["amount"].replace("Rp", "").replace(".", "").replace(",", "").strip() if t["amount"] else "0"
        text += (
            f"{icon} *{t['category']}* {tipe_icon}\n"
            f"   💵 Rp {float(amount_str or 0):,.0f}\n"
            f"   📅 {t['date']} {t['time']}\n"
            f"   📝 {t.get('note', '-') or '-'}\n\n"
        )

    return text


def main():
    sheets_manager.setup_sheets()

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="^type_")],
        states={
            SELECTING_CATEGORY: [CallbackQueryHandler(button_handler, pattern="^cat_")],
            ENTERING_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, amount_handler)
            ],
            ENTERING_NOTE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, note_handler),
                CommandHandler("skip", note_handler),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", lambda u, c: None))
    app.add_handler(CommandHandler("summary", summary_command))
    app.add_handler(CommandHandler("history", history_command))

    clear_handler = ConversationHandler(
        entry_points=[CommandHandler("clear", clear_command)],
        states={
            CLEAR_CONFIRM: [CallbackQueryHandler(clear_confirm_handler, pattern="^clear_")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(clear_handler)
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
