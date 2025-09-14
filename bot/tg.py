from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, Application
from telegram.ext import filters, MessageHandler

from chatgpt import CalorieCounter


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ("Send me a photo of food and I'll tell you how much calories it's worth!" +
            "You can provide any text description with a photo ot help with identification.")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def log_food_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    photo = message.photo

    if photo is None or len(photo) == 0:
        raise RuntimeError("No photo in message")

    max_res_photo = photo[-1]
    file = await max_res_photo.get_file()
    file_bytes = await file.download_as_bytearray()

    client = context.application.bot_data["client"]
    gpt_answer = client.identify_calories(image_bytes=file_bytes, help_text=message.caption)

    if gpt_answer.error:
        text = gpt_answer.error.value + "\n" + gpt_answer.description
    else:
        text = f"{gpt_answer.name}\n\n{gpt_answer.description}\n\nEstimated calories: {gpt_answer.total_calories}"

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def build_app(token: str, api_key: str) -> Application:
    if token is None or api_key is None:
        raise ValueError("Both token and api_key must be provided")

    application = ApplicationBuilder().token(token).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    application.bot_data["client"] = CalorieCounter(api_key=api_key)

    food_handler = MessageHandler(filters.PHOTO, log_food_photo)
    application.add_handler(food_handler)

    return application
