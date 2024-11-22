import os

# Commands and events aren't used but need to be imported to register
from discord_bot.bot import bot
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")


if __name__ == "__main__":
    bot.run(BOT_TOKEN)
