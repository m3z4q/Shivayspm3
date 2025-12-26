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
from telegram.error import RetryAfter, BadRequest

# -------- CONFIG --------
BOT_TOKEN = "8482425122:AAF63Rw-hwVxGYLpPk0y9G2rarIffJkXsrs"

# ONLY 2 OWNERS
OWNERS = {8453291493, 8295675309}

# ⏱️ OFFSET (THIRD BOT)
OFFSET = 1.0

# 🎭 UNIQUE EMOJI THEME (BOT-3)
MASTER_EMOJIS = [
    "🐉","🐲","🦈","🦅","🦁","🐺","🦂","🕷️","🕸️","👁️",
    "⚡","🔥","💥","🌪️","🌩️","☄️","🪐","🌌","☠️","🩸"
]

# -------- AUTO EMOJI GENERATOR --------
def generate_emojis(token: str):
    h = hashlib.sha256(token.encode()).hexdigest()
    random.seed(h)
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
        return
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

# -------- GCNC (HARD UNLIMITED + OFFSET) --------
async def gcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return

    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]:
        return await update.message.reply_text("Group only command.")

    if not context.args:
        return await update.message.reply_text("Usage: /gcnc <group_name>")

    base = " ".join(context.args)

    async def loop():
        emoji_index = 0
        emoji_list = EMOJIS.copy()

        # initial offset so bots rotate safely
        await asyncio.sleep(OFFSET)

        while True:
            try:
                emoji = emoji_list[emoji_index]
                emoji_index = (emoji_index + 1) % len(emoji_list)

                await chat.set_title(f"{emoji} {base}")
                await asyncio.sleep(0.5)  # ⚡ FAST BASE SPEED

            except RetryAfter as e:
                await asyncio.sleep(e.retry_after + 1)

            except BadRequest:
                # same title / minor issue → continue
                await asyncio.sleep(0.3)
                continue

            except asyncio.CancelledError:
                break

            except Exception:
                await asyncio.sleep(2)
                continue

    if chat.id in gcnc_tasks:
        gcnc_tasks[chat.id].cancel()

    gcnc_tasks[chat.id] = context.application.create_task(loop())
    await update.message.reply_text("✅ GCNC started (BOT-3 UNLIMITED + OFFSET)")

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

# -------- WELCOME --------
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
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
