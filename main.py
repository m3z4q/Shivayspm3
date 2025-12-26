import asyncio
import random
import hashlib
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# -------- CONFIG --------
BOT_TOKEN = "8482425122:AAF63Rw-hwVxGYLpPk0y9G2rarIffJkXsrs"

# ONLY 2 OWNERS
OWNERS = {8453291493, 8295675309}

# 🔥 NEW MASTER EMOJI POOL (CHANGED)
MASTER_EMOJIS = [
    "👿","😡","🤡","🦍","🐺","🐍","🦂","🕸️","🕷️","🦇",
    "🌑","🌚","🌒","⚔️","🗡️","🪓","☠️","💣","🔥","🩸"
]

# -------- AUTO EMOJI GENERATOR --------
def generate_emojis(token: str):
    hash_val = hashlib.sha256(token.encode()).hexdigest()
    random.seed(hash_val)
    emojis = MASTER_EMOJIS.copy()
    random.shuffle(emojis)
    return emojis[:8]

EMOJIS = generate_emojis(BOT_TOKEN)

# -------- STORAGE --------
gcnc_tasks = {}

# -------- HELPERS --------
def is_owner(user_id: int) -> bool:
    return user_id in OWNERS

# -------- COMMANDS --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text("❌ Private bot. Access denied.")
    await update.message.reply_text("🤖 Bot Online\nUse /help")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    await update.message.reply_text(
        "/spam <count> <text>\n"
        "/gcnc <group_name>\n"
        "/stopgcnc"
    )

async def spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return

    if len(context.args) < 2:
        return await update.message.reply_text("Usage: /spam <count> <text>")

    count = int(context.args[0])
    text = " ".join(context.args[1:])

    for _ in range(count):
        await update.message.reply_text(text)
        await asyncio.sleep(0.15)

async def gcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    if not is_owner(user.id):
        return

    if chat.type not in ["group", "supergroup"]:
        return await update.message.reply_text("Group only command.")

    if not context.args:
        return await update.message.reply_text("Usage: /gcnc <group_name>")

    base = " ".join(context.args)

    async def loop():
        try:
            while True:
                emoji = random.choice(EMOJIS)
                await chat.set_title(f"{emoji} {base}")
                await asyncio.sleep(2)
        except asyncio.CancelledError:
            pass
        except Exception:
            await asyncio.sleep(5)

    if chat.id in gcnc_tasks:
        gcnc_tasks[chat.id].cancel()

    task = context.application.create_task(loop())
    gcnc_tasks[chat.id] = task

    await update.message.reply_text("✅ GCNC started (emoji auto-rotate)")

async def stopgcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return

    chat = update.effective_chat
    task = gcnc_tasks.pop(chat.id, None)

    if task:
        task.cancel()
        await update.message.reply_text("🛑 GCNC stopped successfully")
    else:
        await update.message.reply_text("No GCNC running.")

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]:
        return
    for member in update.message.new_chat_members:
        await update.message.reply_text(
            f"👋 Welcome {member.mention_html()}!",
            parse_mode="HTML"
        )

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_owner(update.effective_user.id):
        await update.message.reply_text("❓ Unknown command.")

# -------- MAIN --------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("spam", spam))
    app.add_handler(CommandHandler("gcnc", gcnc))
    app.add_handler(CommandHandler("stopgcnc", stopgcnc))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    app.run_polling()

if __name__ == "__main__":
    main()