import logging
import random
import asyncio
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    filters,
)

# === KONFIGURASI ===
BOT_TOKEN = "7942334918:AAFLwMH2NABwkk9kFOrF0vTrXHoe8H_mjuo"
OWNER_ID = 7742582171
SUDO_USERS = [OWNER_ID]
DEV_USERS = [OWNER_ID]

ALLOWED_CHAT = -1002334074368
ALLOWED_THREAD_ID = 38790

EMOJIS = ['😎', '🔥', '🎯', '💥', '✨', '🚀', '👑', '💎']

# === CEK IZIN ===
def is_allowed(update: Update) -> bool:
    if not update.message:
        return False
    chat_id = update.effective_chat.id
    thread_id = update.message.message_thread_id
    return chat_id == ALLOWED_CHAT and thread_id == ALLOWED_THREAD_ID

# === TAG ADMIN SATU PER SATU DENGAN ALASAN ===
async def tag_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        await update.message.reply_text("⛔ Bot hanya bisa digunakan di topik tertentu.")
        return

    reason = " ".join(context.args) if context.args else None

    admins = await context.bot.get_chat_administrators(update.effective_chat.id)
    members = [admin.user for admin in admins if not admin.user.is_bot]

    await update.message.reply_text(
        "🚀 Mulai tag admin satu per satu...",
        reply_to_message_id=update.message.message_id
    )

    for user in members:
        emoji = random.choice(EMOJIS)
        username = f"@{user.username}" if user.username else user.first_name
        mention = f"[{user.first_name}](tg://user?id={user.id})"
        text = f"{emoji} {username} — {mention}"
        if reason:
            text += f"\n🗒️ Alasan: {reason}"
        await update.message.reply_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            message_thread_id=update.message.message_thread_id
        )
        await asyncio.sleep(1)

# === ROLE INFO ===
async def me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == OWNER_ID:
        role = "👑 Owner Bot"
    elif user_id in SUDO_USERS:
        role = "🛠️ Sudo"
    elif user_id in DEV_USERS:
        role = "💻 Developer"
    else:
        role = "👤 Pengguna biasa"

    await update.message.reply_text(
        f"Kamu adalah: <b>{role}</b>",
        parse_mode=ParseMode.HTML,
        reply_to_message_id=update.message.message_id
    )

# === ID CHECKER ===
async def id_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    thread_id = update.message.message_thread_id
    await update.message.reply_text(
        f"Chat ID: <code>{cid}</code>\nThread ID: <code>{thread_id}</code>",
        parse_mode="HTML"
    )

# === START ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Bot aktif!\nGunakan:\n/tag [alasan opsional]\nContoh: /tag ayo kerja bareng!"
    )

# === MAIN ===
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tag", tag_all, filters.ChatType.GROUPS))
    app.add_handler(CommandHandler("me", me))
    app.add_handler(CommandHandler("id", id_check))

    print("Bot aktif...")
    app.run_polling()
