import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

OWNER_ID = 312224589


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌙 Привет.\n\n"
        "Здесь можно анонимно задать вопрос или оставить запрос на расклад.\n\n"
        "Ваше сообщение увидит только Пряник."
    )


async def forward_to_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.id == OWNER_ID:
        return

    sent = await context.bot.send_message(
        chat_id=OWNER_ID,
        text=(
            f"📩 Новый вопрос\n\n"
            f"ID: {user.id}\n\n"
            f"{update.message.text}"
        ),
    )

    context.bot_data[sent.message_id] = user.id

    await update.message.reply_text(
        "✨ Ваш вопрос отправлен. Когда Пряник ответит, вы получите сообщение здесь."
    )


async def reply_from_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if not update.message.reply_to_message:
        return

    original_message_id = update.message.reply_to_message.message_id

    user_id = context.bot_data.get(original_message_id)

    if not user_id:
        return

    await context.bot.send_message(
        chat_id=user_id,
        text="🌙 Ответ на ваш вопрос:\n\n" + update.message.text
    )


def main():
    token = os.getenv("BOT_TOKEN")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.REPLY & ~filters.COMMAND,
            forward_to_owner,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.REPLY,
            reply_from_owner,
        )
    )

    app.run_polling()


if __name__ == "__main__":
    main()
