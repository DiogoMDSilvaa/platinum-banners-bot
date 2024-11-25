import os

# Commands and events aren't used but need to be imported to register
from discord_bot.bot import bot
from discord_bot.events import *
from discord_bot.commands import *
from discord_bot.tasks import *
from dotenv import load_dotenv

from singleton_browser import close_browser_instance

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")


if __name__ == "__main__":
    try:
        bot.run(BOT_TOKEN)
    except:
        close_browser_instance()
