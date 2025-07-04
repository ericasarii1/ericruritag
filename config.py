import logging
import random
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    filters,
)

# === KONFIGURASI ===
BOT_TOKEN = "YOUR_BOT_TOKEN"
OWNER_ID = 123456789  # ganti ke user ID kamu
SUDO_USERS = [OWNER_ID]
DEV_USERS = [OWNER_ID]

ALLOWED_CHAT = -1001234567890       # ID grup kamu
ALLOWED_THREAD_ID = 123             # ID topik/thread (opsional)

EMOJIS = ['😎', '🔥', '🎯', '💥', '✨', '🚀', '👑', '💎']

# === CEK IZIN ===
def is_allowed(update: Update) -> bool:
    if not update.message:
        return False

    chat_id = update.effective_chat.id
    thread_id = update.message.message_thread_id
    return chat_id == ALLOWED_CHAT and thread_id == ALLOWED_THREAD_ID

# === TAG COMMAND ===
async def tag_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        await update.message.reply_text("⛔ Bot hanya bisa digunakan di topik tertentu.")
        return

    members = []
    async for member in context.bot.get_chat_administrators(update.effective_chat.id):
        if not member.user.is_bot:
            members.append(member.user)

    mentions = []
    for user in members:
        emoji = random.choice(EMOJIS)
        mention = f"{emoji} [{user.first_name}](tg://user?id={user.id})"
        mentions.append(mention)

    text = "🔥 *TAG SEMUA ADMIN:*\n" + "\n".join(mentions)
    await update.message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_to_message_id=update.message.message_id
    )

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
    await update.message.reply_text(f"Chat ID: <code>{cid}</code>\nThread ID: <code>{thread_id}</code>", parse_mode="HTML")

# === START ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot aktif!\nGunakan /tag untuk mention semua admin.")

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
