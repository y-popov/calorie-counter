import logging
import os

from tg import build_app

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    app = build_app(
        token=os.getenv("TELEGRAM_BOT_TOKEN"),
        api_key=os.getenv("OPENAI_API_KEY")
    )

    app.run_polling()
