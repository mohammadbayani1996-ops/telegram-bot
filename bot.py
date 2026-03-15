from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import sqlite3

TOKEN = "8571831791:AAFTZFJaytKS8djih7ZwVadw2kykGnVyHug"

ADMIN_ID = 1881337130

CHANNEL = "@sateki_khosh2"

CHANNELS = [
    "@sateki_khosh2",
    "@qsaie_khosh",
    "@sateki_khosh22",
    "@nesteq_beserhati"
]

db = sqlite3.connect("music.db", check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS songs(
code TEXT,
file_id TEXT,
downloads INTEGER
)
""")

db.commit()


async def check_member(user_id, bot):

    for channel in CHANNELS:

        member = await bot.get_chat_member(channel, user_id)

        if member.status not in ["member","administrator","creator"]:

            return False

    return True


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if not await check_member(user_id, context.bot):

        keyboard = [
            [InlineKeyboardButton("🎧 ساتێکی خۆش", url="https://t.me/sateki_khosh2")],
            [InlineKeyboardButton("😹 قسەی خۆش", url="https://t.me/qsaie_khosh")],
            [InlineKeyboardButton("🎵 Sateki Khosh Music", url="https://t.me/sateki_khosh22")],
            [InlineKeyboardButton("📚 با قسەی خۆش ون نەبێت", url="https://t.me/nesteq_beserhati")],
            [InlineKeyboardButton("✅ من عضو شدم", url="https://t.me/Sateki_Khosh2bot")]
        ]

        text = """
°•✨ ساتــێـکے ♫︎خــۆش ✨•°

👋 بەخێربێیت
بۆ بەدەستهێنانی گۆرانی تکایە سەرەتا ببە بە ئەندامی کەناڵەکان 👇
"""

        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return


    if context.args:

        code = context.args[0]

        cursor.execute("SELECT file_id FROM songs WHERE code=?", (code,))
        data = cursor.fetchone()

        if data:

            keyboard = [
                [InlineKeyboardButton("📥 دانلود کامل", callback_data=code)]
            ]

            await update.message.reply_text(
                "🎧 گۆرانییەکی نوێ\n\nبۆ داگرتن کلیک بکە ⬇️",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        else:

            await update.message.reply_text("❌ گۆرانی نەدۆزرایەوە")

    else:

        await update.message.reply_text("🎧 بەخێربێیت بۆ رباتی ساتێکی خۆش")


async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    code = query.data

    cursor.execute("SELECT file_id,downloads FROM songs WHERE code=?", (code,))
    data = cursor.fetchone()

    if data:

        file_id, downloads = data

        downloads += 1

        cursor.execute(
            "UPDATE songs SET downloads=? WHERE code=?",
            (downloads, code)
        )

        db.commit()

        await query.message.reply_audio(
            file_id,
            caption=f"📥 دانلود شد\n👥 تعداد دانلود: {downloads}"
        )

    await query.answer()


async def upload_song(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    audio = update.message.audio.file_id

    cursor.execute("SELECT COUNT(*) FROM songs")
    count = cursor.fetchone()[0] + 1

    code = str(count)
