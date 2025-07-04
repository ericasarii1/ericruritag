import logging
import random
import asyncio
import html
from telegram import Update, ChatMember, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode, ChatMemberStatus
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

tagging_sessions = {}

# === CEK IZIN ===
def is_allowed(update: Update) -> bool:
    if not update.message:
        return False
    chat_id = update.effective_chat.id
    thread_id = update.message.message_thread_id
    return chat_id == ALLOWED_CHAT and thread_id == ALLOWED_THREAD_ID

# === Cek Role ===
def is_bot_admin(user_id: int) -> bool:
    return user_id == OWNER_ID or user_id in SUDO_USERS or user_id in DEV_USERS

async def is_user_admin(update: Update, user_id: int) -> bool:
    try:
        member: ChatMember = await update.effective_chat.get_member(user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return False

# === TAG FUNCTION ===
async def tag_users(update: Update, context: ContextTypes.DEFAULT_TYPE, target_admins=True):
    if not is_allowed(update):
        await update.message.reply_text("⛔ Bot hanya bisa digunakan di topik tertentu.")
        return

    chat_id = update.effective_chat.id
    thread_id = update.message.message_thread_id or (
        update.message.reply_to_message.message_thread_id if update.message.reply_to_message else None
    )
    session_key = (chat_id, thread_id)

    if tagging_sessions.get(session_key, False):
        await update.message.reply_text("⚠️ Proses tagging masih berjalan.")
        return

    tagging_sessions[session_key] = True
    await context.bot.send_message(
        chat_id=chat_id,
        text="🚀 Memulai proses tag...",
        message_thread_id=thread_id
    )

    try:
        if target_admins:
            admins = await context.bot.get_chat_administrators(chat_id)
            users = [admin.user for admin in admins if not admin.user.is_bot]
        else:
            # fallback ke admin juga (karena fetch semua member tidak tersedia)
            admins = await context.bot.get_chat_administrators(chat_id)
            users = [admin.user for admin in admins if not admin.user.is_bot]

        delay = 2 if len(users) > 30 else 1.5 if len(users) > 10 else 1

        for user in users:
            await asyncio.sleep(0)
            if not tagging_sessions.get(session_key):
                break

            emoji = random.choice(EMOJIS)
            display_name = html.escape(user.full_name or "Pengguna")
            mention = f"<a href='tg://user?id={user.id}'>{display_name}</a>"
            username = f"@{user.username}" if user.username else display_name

            text = f"{emoji} {username} — {mention}"

            # Tombol link ke pesan awal
            try:
                message_url = f"https://t.me/c/{str(chat_id)[4:]}/{update.message.message_id}"
                buttons = InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔗 Lihat Pesan", url=message_url)
                ]])
            except:
                buttons = None

            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                    message_thread_id=thread_id,
                    reply_markup=buttons
                )
            except Exception as e:
                logging.warning(f"❌ Gagal kirim ke {user.id}: {e}")
            await asyncio.sleep(delay)

    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"❌ Gagal: <code>{html.escape(str(e))}</code>",
            parse_mode=ParseMode.HTML,
            message_thread_id=thread_id
        )
    finally:
        tagging_sessions[session_key] = False
        await context.bot.send_message(
            chat_id=chat_id,
            text="✅ Proses tag selesai.",
            message_thread_id=thread_id
        )

# === COMMAND ===
async def tag_admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await tag_users(update, context, target_admins=True)

async def tag_all_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await tag_users(update, context, target_admins=False)

async def me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == OWNER_ID:
        role = "👑 Owner Bot"
    elif user_id in SUDO_USERS:
        role = "🛠️ Sudo"
    elif user_id in DEV_USERS:
        role = "💻 Developer"
    else:
        is_admin_grup = await is_user_admin(update, user_id)
        role = "👮 Admin Grup" if is_admin_grup else "👤 Pengguna biasa"
    await update.message.reply_text(f"Kamu adalah: <b>{role}</b>", parse_mode=ParseMode.HTML)

async def id_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    thread_id = update.message.message_thread_id
    await update.message.reply_text(f"Chat ID: <code>{cid}</code>\nThread ID: <code>{thread_id}</code>", parse_mode="HTML")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Bot aktif!\nGunakan:\n"
        "/tag — tag admin\n"
        "/tagall — tag semua member\n"
        "/me — cek role kamu\n"
        "/id — lihat chat ID dan thread ID"
    )

# === MAIN ===
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tag", tag_admin_cmd, filters.ChatType.GROUPS))
    app.add_handler(CommandHandler("tagall", tag_all_cmd, filters.ChatType.GROUPS))
    app.add_handler(CommandHandler("me", me))
    app.add_handler(CommandHandler("id", id_check))

    print("Bot aktif...")
    app.run_polling()
