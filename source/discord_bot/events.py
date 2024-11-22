""" Contains the methods corresponding to bot events """

from discord.ext import commands
from utils import create_bot_category, create_channel, delete_bot_category

from .bot import bot, db
from .tasks import update_banners

# When the bot loses WIFI connection, it runs `on_ready` again after reconnecting
# creating all the channels and etc, so use this flag to avoid that
already_started_up = False


@bot.event
async def on_ready():
    """Starts the bot and creates the channels"""

    global already_started_up

    if not already_started_up:
        print(f"Logged in as {bot.user}, starting up...")

        # Only create the channels and etc if there isn't a backup
        # (for example in a power cut, the bot shouldn't recreate everything, just resume activity from the previous state)
        if not db.try_load_backup():
            for guild in bot.guilds:

                # Clean up
                await delete_bot_category(guild)

                print(f"Initializing guild '{guild.name}'")

                # Create category and manage channel
                await create_bot_category(guild)
                channel = await create_channel(
                    guild=guild, channel_name="Manage", allow_user_messages=True
                )

                # Display hello message and commands
                ctx = await bot.get_context(
                    await channel.send("Hello! Ready to track the players...")
                )
                await bot.get_command("help").invoke(ctx)

        # Start the update banners task
        if not update_banners.is_running():
            update_banners.start()

        already_started_up = True


@bot.event
async def on_command_error(ctx, error):
    """Displays help message when there is an error"""

    if isinstance(error, commands.CheckFailure):
        return  # If there was a check failure nothing should be done, the bot just won't respond
    else:
        ctx = await bot.get_context(await ctx.send("Oops! Something wasn't right..."))
        await bot.get_command("help").invoke(ctx)
