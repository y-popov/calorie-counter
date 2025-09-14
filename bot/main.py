import asyncio
import flask
import logging
import os
import functions_framework

from typing import Optional
from telegram import Update
from telegram.ext import Application

from tg import build_app

logging.basicConfig(level=logging.INFO)

# Global application and event loop for Google Cloud Functions
_application: Optional[Application] = None
_app_initialized: bool = False
_loop: Optional[asyncio.AbstractEventLoop] = None


def _get_loop() -> asyncio.AbstractEventLoop:
    global _loop
    if _loop is None or _loop.is_closed():
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)
    return _loop


def _get_application():
    """Create and initialize the Telegram Application once per cold start."""
    global _application, _app_initialized

    if _application is None:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        api_key = os.getenv("OPENAI_API_KEY")
        if not token or not api_key:
            raise RuntimeError("Missing TELEGRAM_BOT_TOKEN or OPENAI_API_KEY environment variables")
        _application = build_app(token=token, api_key=api_key)

    if not _app_initialized:
        loop = _get_loop()
        loop.run_until_complete(_application.initialize())
        _app_initialized = True

    return _application


@functions_framework.http
def telegram_webhook(request: flask.Request):
    try:
        if request.method != "POST":
            logging.error("Received request with method %s", request.method)
            return "Method Not Allowed", 405

        data = request.get_json(silent=True)
        if not data:
            logging.error("Received request with no JSON payload")
            return "Bad Request: no JSON payload", 400

        application = _get_application()
        update = Update.de_json(data, application.bot)

        loop = _get_loop()
        loop.run_until_complete(application.process_update(update))

        return "", 204

    except Exception as e:
        logging.exception("Error handling webhook: %s", e)
        return "Internal Server Error", 500


if __name__ == '__main__':
    from dotenv import load_dotenv

    load_dotenv()

    app = build_app(
        token=os.getenv("TELEGRAM_BOT_TOKEN"),
        api_key=os.getenv("OPENAI_API_KEY")
    )

    app.run_polling()
