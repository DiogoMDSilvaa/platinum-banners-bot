import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from io import BytesIO
from typing import Set

import requests
from bs4 import BeautifulSoup
from PIL import Image
from singleton_browser import get_browser_page

from .game import Console, Game
from .platinum import Platinum


@dataclass
class Player:
    """Represents a player"""

    gamer_tag: str

    games_with_platinum: Set[Game] = field(default_factory=set)

    async def get_new_platinums_banners(self, discord_ctx) -> list:
        """Returns the banners of the newly achieved platinums"""

        sleep_seconds = 10

        discord_message = await discord_ctx.send(
            f"Waiting for {self.gamer_tag} PSN profile update ({sleep_seconds} seconds)"
        )

        await self.__update_psn_profile(sleep_seconds=sleep_seconds)

        await discord_message.edit(content=f"Updated {self.gamer_tag} PSN profile")

        new_platinums_banner = []

        page = await get_browser_page()

        await page.goto(f"https://psnprofiles.com/{self.gamer_tag}")
        await asyncio.sleep(0.1)

        # Retrieve all games with platinum
        profile_page_soup = BeautifulSoup(await page.content(), "lxml")
        games_table = profile_page_soup.find(id="gamesTable").tbody
        games_with_platinum = games_table.find_all("tr", class_="platinum")

        games_with_platinum.reverse()  # Chronological order

        for i, game in enumerate(games_with_platinum):

            # Scrape the information needed to create the game object
            tds = game.find_all("td")
            anchor = tds[1].div.span.a

            name = anchor.text
            game_id = anchor["href"].split("/")[2]
            console = Console[tds[2].span.div.find("span").text]

            date = tds[1].find_all("div")[-1].text.split("•")[0].strip()
            space_index = date.index(" ")
            date = datetime.strptime(
                date[: space_index - 2] + date[space_index:], "%d %B %Y"
            )

            game = Game(id=game_id, name=name, console=console)

            # Retrieve platinum info and generate banner
            if game not in self.games_with_platinum:
                await discord_message.edit(
                    content=f"Progress ({i+1}/{len(games_with_platinum)}) - Generating banner for '{game.name}'"
                )

                # Go to game trophies page to get the link of the guide page
                await page.goto(
                    f"https://psnprofiles.com/trophies/{game.id}/{self.gamer_tag}"
                )
                await asyncio.sleep(0.1)
                game_trophies_soup = BeautifulSoup(await page.content(), "lxml")

                # Retrieve game banner
                banner_url = (
                    game_trophies_soup.find(id="first-banner")
                    .find_all("div")[-1]["style"]
                    .split("url(")[-1][:-1]
                )
                banner_response = requests.get(banner_url)
                await asyncio.sleep(0.1)
                image_data = BytesIO(banner_response.content)
                game.banner = Image.open(image_data)

                # Go to the guide page to get the platinum information
                guide_link = game_trophies_soup.find("div", class_="guide-page-info")

                platinum_hours = None
                platinum_playthroughs = None
                platinum_difficulty = None

                # If it has a guide, retrieve information
                if guide_link is not None:

                    await page.goto(f'https://psnprofiles.com{guide_link.a["href"]}')
                    await asyncio.sleep(0.1)
                    guide_soup = BeautifulSoup(await page.content(), "lxml")

                    platinum_info_spans = guide_soup.find(
                        "div", class_="overview-info"
                    ).find_all("span", recursive=False)

                    platinum_difficulty = int(
                        platinum_info_spans[0].find("span").text.split("/")[0]
                    )
                    platinum_playthroughs = int(
                        platinum_info_spans[1].find("span").text
                    )
                    platinum_hours = int(platinum_info_spans[2].find("span").text)

                platinum = Platinum(
                    difficulty=platinum_difficulty,
                    playthroughs=platinum_playthroughs,
                    hours=platinum_hours,
                    date_earned=date,
                )
                game.platinum = platinum

                # Update games list and generate banner
                self.games_with_platinum.add(game)
                new_platinums_banner.append(game.create_platinum_banner())
                print(f"Created banner of game {game.name} for {self.gamer_tag}")
            else:
                await discord_message.edit(
                    content=f"Progress ({i+1}/{len(games_with_platinum)}) - '{game.name}' is not a new platinum"
                )

        return new_platinums_banner

    async def __update_psn_profile(self, sleep_seconds) -> None:
        """Updates the PSNProfile so that the latest trophy information can be extracted"""

        page = await get_browser_page()

        await page.goto("https://psnprofiles.com/")

        # Find the text input field by id and type gamer tag
        await page.type("#psnId", self.gamer_tag)

        # CLick on the green "Update User" button
        await page.evaluate(
            """() => {
            document.querySelector("a.button.green[onclick*='updatePsnUser']").click();
        }"""
        )

        print(f"Updating {self.gamer_tag} profile, sleeping {sleep_seconds} seconds...")
        await asyncio.sleep(sleep_seconds)
