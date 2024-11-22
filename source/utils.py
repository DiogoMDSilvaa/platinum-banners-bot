""" Contains async utility functions """

from io import BytesIO

import discord
from constants import CATEGORY_NAME
from discord import CategoryChannel, Guild, TextChannel
from PIL.Image import Image

#################### Async ####################


async def create_bot_category(guild: Guild) -> CategoryChannel:
    """Creates the bot category in the current `guild`"""

    category = discord.utils.get(guild.categories, name=CATEGORY_NAME)

    if category is None:
        category = await guild.create_category(CATEGORY_NAME)
        print(f"Category '{CATEGORY_NAME}' was created")
    else:
        print(f"Category '{CATEGORY_NAME}' already exists, skipping creation")

    return category


async def create_channel(
    guild: Guild, channel_name: str, allow_user_messages=False
) -> TextChannel:
    """Creates a channel with `channel_name` in the current `guild` (under the bot category)"""

    channel_name = format_channel_name(channel_name)

    category = discord.utils.get(guild.categories, name=CATEGORY_NAME)

    # Bot category didn't exist, create it
    if category is None:
        category = await create_bot_category(guild=guild)

    existing_channel = discord.utils.get(category.channels, name=channel_name)

    if existing_channel is None:

        # Set permissions of the channel
        # The bot will have an interactive channel and the rest are only informative so the user can't write there
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                send_messages=allow_user_messages,
                view_channel=True,
                read_message_history=True,
            ),
            guild.me: discord.PermissionOverwrite(send_messages=True),
        }

        existing_channel = await guild.create_text_channel(
            channel_name, category=category, overwrites=overwrites
        )
        print(f"Channel '{channel_name}' was created")
    else:
        print(f"Channel '{channel_name}' already exists, skipping creation")

    return existing_channel


async def delete_bot_category(guild: Guild):
    """Deletes the bot category and all the channels"""

    category = discord.utils.get(guild.categories, name=CATEGORY_NAME)

    if category is not None:

        for channel in category.channels:
            await channel.delete()

        await category.delete()
        print(f"Category '{CATEGORY_NAME}' was deleted")
    else:
        print(f"Category '{CATEGORY_NAME}' didn't exist, skipping deletion")


async def delete_channel(guild: Guild, channel_name: str) -> TextChannel:
    """Deletes a channel with `channel_name` in the current `guild` (under the bot category)"""

    channel_name = format_channel_name(channel_name)

    category = discord.utils.get(guild.categories, name=CATEGORY_NAME)

    if category is None:
        print(
            f"Category '{CATEGORY_NAME}' didn't exist, skipping channel '{channel_name}' deletion"
        )
        return

    existing_channel = discord.utils.get(category.channels, name=channel_name)

    if existing_channel is not None:
        await existing_channel.delete()
        print(f"Channel '{channel_name}' was deleted")
    else:
        print(f"Channel '{channel_name}' didn't exist, skipping deletion")


async def get_channel(guild: Guild, channel_name: str) -> TextChannel:
    """Returns the channel with `channel_name` inside the bot category"""

    channel_name = format_channel_name(channel_name)

    category = discord.utils.get(guild.categories, name=CATEGORY_NAME)

    if category is None:
        raise ValueError("Can't retrieve channel as category didn't exist.")

    existing_channel = discord.utils.get(category.channels, name=channel_name)

    if existing_channel is not None:
        return existing_channel
    else:
        raise ValueError(f"Can't retrieve channel as '{channel_name}' didn't exist.")


async def send_new_banners(channel: TextChannel, banners: list[Image]):
    """Send the messages with the latest user banners"""

    for index, banner in enumerate(banners):
        # Convert banner to binary format (BytesIO) if it's not already in binary format
        if not isinstance(banner, bytes):
            banner_file = BytesIO()
            banner.save(banner_file, format="PNG")
            banner_file.seek(0)  # Rewind the buffer to the beginning
        else:
            banner_file = BytesIO(banner)

        filename = f"banner_{index}.png"

        file = discord.File(banner_file, filename=filename)

        await channel.send(file=file)


#################### Sync ####################


def format_channel_name(channel_name: str) -> str:
    """Formats the desired channel name to the name given by Discord"""

    return channel_name.replace(" ", "-").lower()
