import os
import time

import openai
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

def check_run(client, thread_id, run_id):
    while True:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )

        if run.status == "completed":
            return run
        elif run.status == "expired":
            return None
        else:
            time.sleep(1)

def handle_message(update: Update, context: CallbackContext, client, thread, assistant) -> None:
    user_input = update.message.text

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    run = check_run(client, thread.id, run.id)

    if run is not None:
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )

        assistant_message = messages.data[0].content[0].text.value

        update.message.reply_text(assistant_message)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Приветствие")

def main():
    load_dotenv(override=True, dotenv_path=".env")
    openai.api_key = os.getenv("OPENAI_API_KEY")
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")

    client = openai.Client()

    existing_assistants = client.beta.assistants.list()
    existing_assistant = next((assistant for assistant in existing_assistants.data if assistant.id == "asst_5h5SOuRkeAtCrzmiY4kVSat0"), None)

    if existing_assistant is None:
        print("The existing assistant was not found.")
        return

    thread = client.beta.threads.create()

    updater = Updater(token=telegram_token)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, lambda update, context: handle_message(update, context, client, thread, existing_assistant)))

    updater.start_polling()

    updater.idle()


if __name__ == "__main__":
    main()