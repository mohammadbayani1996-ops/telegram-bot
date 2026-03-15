cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-t", "20",
        output_path
    ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ======================
# آپلود آهنگ توسط ادمین
# ======================

async def upload_song(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    audio = update.message.audio
    file = await context.bot.get_file(audio.file_id)

    tmp_input = tempfile.mktemp(".mp3")
    tmp_output = tempfile.mktemp(".mp3")

    await file.download_to_drive(tmp_input)

    try:
        create_preview(tmp_input, tmp_output)
        preview_file = open(tmp_output,"rb")
    except:
        preview_file = None

    cursor.execute("SELECT COUNT(*) FROM songs")
    count = cursor.fetchone()[0] + 1

    code = str(count)

    cursor.execute("INSERT INTO songs VALUES(?,?,?)",(code,audio.file_id,0))
    db.commit()

    link = f"https://t.me/Sateki_Khosh2bot?start={code}"

    keyboard = [[InlineKeyboardButton("📥 دانلود کامل", url=link)]]

    await context.bot.send_audio(
        chat_id=CHANNEL,
        audio=preview_file if preview_file else audio.file_id,
        caption="""
🎧 گۆرانییەکی نوێ

🔊 Preview 20s

بۆ داگرتنی تەواو
کلیک لە خوارەوە ⬇️
""",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await update.message.reply_text(f"✅ پست شد\n{link}")

# ======================
# پنل ادمین
# ======================

async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    keyboard = [
        [InlineKeyboardButton("📊 آمار", callback_data="stats")],
        [InlineKeyboardButton("📢 زمانبندی پست", callback_data="schedule")]
    ]

    await update.message.reply_text(
        "📋 پنل مدیریت",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ======================
# آمار
# ======================

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    cursor.execute("SELECT COUNT(*) FROM songs")
    songs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users")
    users = cursor.fetchone()[0]

    text = f"""
📊 آمار ربات

👥 کاربران: {users}
🎵 آهنگ‌ها: {songs}
"""

    await query.message.edit_text(text)

# ======================
# زمانبندی پست
# ======================

async def schedule_post(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.callback_query.message.reply_text(
        "برای زمانبندی:\n\n/send 60\n\nیعنی 60 دقیقه بعد پست شود"
    )

# ======================
# اجرای ربات
# ======================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("panel", panel))

app.add_handler(MessageHandler(filters.AUDIO, upload_song))

app.add_handler(CallbackQueryHandler(check_button, pattern="check"))
app.add_handler(CallbackQueryHandler(download))
app.add_handler(CallbackQueryHandler(stats, pattern="stats"))
app.add_handler(CallbackQueryHandler(schedule_post, pattern="schedule"))

print("Bot running...")

app.run_polling()
