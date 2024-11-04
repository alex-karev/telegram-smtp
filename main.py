#!.env/bin/python
import logging
from time import sleep
from telegram.ext import filters, ApplicationBuilder, CommandHandler
import json
from smtp import SMTP
from database import find_chat, update_user
from middleware import catch_errors, use_auth, use_context_args, api_call
import asyncio

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Load settings
with open("settings.json", "r") as f:
    settings = json.loads(f.read())

# Load language
with open("lang.json", "r") as f:
    lang = json.loads(f.read())[settings["app"]["lang"]]
    help_message = settings["app"]["greetings"].format(help=lang["help_message"])

# Show greetings
@catch_errors
@api_call
async def start():
    return help_message

# Show help
@catch_errors
@api_call
async def help():
    return help_message

# Update user
@catch_errors
@use_auth
@use_context_args
@api_call
async def register(chat_id: int, context_args):
    if len(context_args) != 1:
        return lang["invalid_email"]
    email = context_args[0]
    user = update_user(chat_id, email)
    if not user:
        return lang["email_taken"]
    return lang["email_updated"]

# Send messages using bot
async def send(app, source, targets, subject, message):
    for target in targets:
        chat_id = find_chat(target)
        if not chat_id: #type: ignore
            return
        resp = settings["app"]["message"].format(source=source, target=target, subject=subject, message=message)
        await app.bot.send_message(chat_id=chat_id, text=resp)
        logging.info("Message forwarded to telegram chat: {} ({})".format(chat_id, target))

# Create new Telegram bot
def create_bot():
    application = ApplicationBuilder().token(settings["telegram"]["api_token"])
    if settings["telegram"]["proxy"]:
        application = application.proxy(settings["telegram"]["proxy"]).get_updates_proxy(settings["telegram"]["proxy"])
    application = application.build()
    return application

# Forward loop that forwards messages from smtp to telegram
async def forward_loop():
    # Initialize bot
    app = create_bot()
    # Initialize SMTP server
    smtp = SMTP(
        **settings["smtp"], 
        check_id=find_chat, 
        callback=lambda source, targets, subject, message: send(app, source, targets, subject, message)
    )
    # Start smtp server
    smtp.start()
    # Keep the server running until interrupted
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        pass
    # Shutdown
    smtp.stop()

# Command loop for sending commands to the bot
async def command_loop():
    # Build bot
    app = create_bot()
    # Add commands
    app.add_handler(CommandHandler('start', start)) #type: ignore
    app.add_handler(CommandHandler('help', help)) #type: ignore
    app.add_handler(CommandHandler('register', register)) #type: ignore
    # Start bot
    await app.initialize()
    await app.start()
    await app.updater.start_polling() #type: ignore
    # Keep the server running until interrupted
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        pass
    # Shutdown
    await app.updater.stop() #type: ignore
    await app.stop()
    await app.shutdown()

# Main function
async def main():
    await asyncio.gather(forward_loop(), command_loop())

# Entry
if __name__ == "__main__":
    asyncio.run(main())
