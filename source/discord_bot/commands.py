""" Contains the commands the bot answers to """

from datetime import datetime
from functools import wraps

from constants import CATEGORY_NAME, MANAGE_CHANNEL, UPDATE_INTERVAL
from discord.ext import commands
from utils import create_channel, delete_channel, get_channel, send_new_banners

from classes.player import Player
from .bot import bot, db

# Flag to avoid running multiple commands at the same time
processing_command = False


def handle_processing_flag(func):
    """Decorator to set/unset the flag while running a command"""

    @wraps(func)
    async def wrapper(ctx, *args, **kwargs):
        global processing_command

        if processing_command:
            await ctx.send("I'm already processing another command. Please wait.")
            return

        processing_command = True
        try:
            return await func(ctx, *args, **kwargs)
        finally:
            processing_command = False

    return wrapper


def should_answer_command(ctx):
    """Checks if the bot should answer the command"""
    return (
        ctx.channel.category
        and ctx.channel.category.name
        == CATEGORY_NAME  # Should be inside the bot category
        and ctx.channel.name == MANAGE_CHANNEL  # and on the manage channel
    )


@bot.command()
@commands.check(should_answer_command)
@handle_processing_flag
async def help(ctx):
    """Displays bot commands"""

    help_text = f"""
**My Commands:**

`$help` 
- *See this message.*

`$tracked` 
- *Returns the list of the players being tracked in this server.*

`$add <player_game_tag>` 
- *Starts tracking the platinums of the player defined by `player_game_tag`.* 

`$remove <player_game_tag>` 
- *Stops tracking the platinums of the player with `player_game_tag`.* 
- *The name should be the same name used in the output of `$tracked`.*

`$update` 
- *Triggers a manual update of the banners (they update automatically every {UPDATE_INTERVAL} minutes).*
"""

    await ctx.send(help_text)


@bot.command()
@commands.check(should_answer_command)
@handle_processing_flag
async def tracked(ctx):
    """Display the current tracked players"""

    players: list[Player] = db.get_players_list()

    if len(players) == 0:
        await ctx.send(
            "Currently there aren't any players being tracked. Add some using `$add`."
        )
    else:
        text = "**Players being tracked:**\n" + "\n".join(
            [f"- {player.gamer_tag}" for player in players]
        )

        await ctx.send(text)


@bot.command()
@commands.check(should_answer_command)
@handle_processing_flag
async def add(ctx, new_gamer_tag: str):
    """Adds a player"""

    try:

        # Add player and create player channel
        player = db.add_player(new_gamer_tag=new_gamer_tag)
        await ctx.send("Adding player...")
        channel = await create_channel(guild=ctx.guild, channel_name=player.gamer_tag)

        # Get the banners changes and send the messages
        banners = await player.get_new_platinums_banners(discord_ctx=ctx)

        await send_new_banners(channel=channel, banners=banners)

        await ctx.send("Player added. Check the new channel with the banners.")

    except Exception as e:
        await ctx.send(e)
    finally:
        db.save_backup()


@bot.command()
@commands.check(should_answer_command)
@handle_processing_flag
async def remove(ctx, gamer_tag: str):
    """Removes a player"""

    try:

        # Removes a player and deletes player channel
        db.remove_player(gamer_tag=gamer_tag)
        await ctx.send("Removing player...")
        await delete_channel(guild=ctx.guild, channel_name=gamer_tag)

        await ctx.send("Player removed.")

    except Exception as e:
        await ctx.send(str(e) + "\n")

        await bot.get_command("tracked").invoke(ctx)
    finally:
        db.save_backup()


@bot.command()
@commands.check(should_answer_command)
@handle_processing_flag
async def update(ctx):
    """Updates the banners of each player"""

    manage_channel = await get_channel(guild=ctx.guild, channel_name=MANAGE_CHANNEL)

    n_new_banners = 0
    for player in db.get_players_list():
        await manage_channel.send(f"Updating {player.gamer_tag}...")

        banners = await player.get_new_platinums_banners(discord_ctx=ctx)
        await send_new_banners(
            channel=await get_channel(guild=ctx.guild, channel_name=player.gamer_tag),
            banners=banners,
        )

        n_new_banners += len(banners)

    await manage_channel.send(
        f"Updated banners @ {datetime.now().strftime('%H:%M of %d/%m/%Y')} **({n_new_banners} new banners)**"
    )
