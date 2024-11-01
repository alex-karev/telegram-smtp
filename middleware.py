from telegram import Update, Message, User 
from telegram.ext import ContextTypes
from telegram.constants import ChatType

# Catch errors in backend
def catch_errors(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
        if update.effective_chat:
            try:
                return await func(update=update, context=context, **kwargs)
            except Exception as e:
                response = "[Error! Exception code: '{}']".format(str(e.args[0]) if len(e.args) > 0 else e)
                await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    return wrapper

# Check message and extract chat id
def use_auth(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
        # Check message
        if not update.message:
            raise Exception("invalid_message")
        message: Message = update.message
        # Check user and text
        if not message.from_user:
            raise Exception("invalid_user")
        user: User = message.from_user
        # Ignore group chats
        if message.chat.type != ChatType.PRIVATE:
            raise Exception("group_chats_are_not_supported")
        # Ignore bots
        if user.is_bot:
            raise Exception("bots_are_not_welcome")
        # Run main function
        return await func(update=update, context=context, chat_id=user["id"], **kwargs)
    return wrapper

# Pass context arguments to the function
def use_context_args(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
        return await func(update=update, context=context, context_args=context.args, **kwargs)
    return wrapper

# Strip from update and context to simplify API calls
def api_call(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
        if update.effective_chat:
            response = await func(**kwargs)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    return wrapper

