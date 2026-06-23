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
        "Привет, это пространство для тихих вопросов и запросов на расклад.\n\n"
        "Можно попросить карту дня, совет от карт, расклад на ситуацию, внутреннее состояние или просто выговориться без карт.\n\n"
        "Не обязательно знать, как правильно формулировать запрос — можно просто рассказать свою историю или написать всё так, как чувствуется.\n\n"
        "Просто напиши то, что сейчас важно для тебя 🌙"
    )


async def forward_to_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.id == OWNER_ID:
        return

    sent = await context.bot.send_message(
        chat_id=OWNER_ID,
        text=(
            f"📩 Новый вопрос\n\n"
            f"{update.message.text}"
        ),
    )

    context.bot_data[sent.message_id] = user.id

    await update.message.reply_text(
        "✨ Спасибо, я получила твой вопрос!\n\n"
        "Когда я познакомлюсь с ним и подготовлю ответ, "
        "ты получишь сообщение в этом чате 🌙"
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

    # Ответ текстом
    if update.message.text:
        await context.bot.send_message(
            chat_id=user_id,
            text="🌙 Ответ на твой вопрос:\n\n" + update.message.text
        )

    # Ответ фото с подписью
    elif update.message.photo:
        photo = update.message.photo[-1].file_id

        await context.bot.send_photo(
            chat_id=user_id,
            photo=photo,
            caption=update.message.caption or ""
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
            filters.REPLY,
            reply_from_owner,
        )
    )

    app.run_polling()


if __name__ == "__main__":
    main()
