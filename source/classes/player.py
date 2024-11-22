import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from io import BytesIO
from typing import Set

from bs4 import BeautifulSoup
from PIL import Image
from pyppeteer import launch
from requests_html import AsyncHTMLSession

from .game import Console, Game
from .platinum import Platinum
from utils import running_in_raspberry_pi
from constants import CHROMIUM_RASPBERRY_PATH


@dataclass
class Player:
    """Represents a player"""

    gamer_tag: str

    games_with_platinum: Set[Game] = field(default_factory=set)

    async def get_new_platinums_banners(self) -> list:
        """Returns the banners of the newly achieved platinums"""

        await self.update_psn_profile()

        new_platinums_banner = []

        # Load user profile page and render the games asynchronously
        session = AsyncHTMLSession()

        # Specify path in raspberry pi
        if running_in_raspberry_pi():
            session.browser_args = {"executablePath": CHROMIUM_RASPBERRY_PATH}

        response = await session.get(f"https://psnprofiles.com/{self.gamer_tag}")
        await response.html.arender()
        await asyncio.sleep(0.1)

        # Retrieve all games with platinum
        profile_page_soup = BeautifulSoup(response.html.html, "lxml")
        games_table = profile_page_soup.find(id="gamesTable").tbody
        games_with_platinum = games_table.find_all("tr", class_="platinum")

        for game in games_with_platinum:

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

                # Go to game trophies page to get the link of the guide page
                response = await session.get(
                    f"https://psnprofiles.com/trophies/{game.id}/{self.gamer_tag}"
                )
                await response.html.arender()
                await asyncio.sleep(0.1)
                game_trophies_soup = BeautifulSoup(response.html.html, "lxml")

                # Retrieve game banner
                banner_url = (
                    game_trophies_soup.find(id="first-banner")
                    .find_all("div")[-1]["style"]
                    .split("url(")[-1][:-1]
                )
                banner_response = await session.get(banner_url)
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

                    guide_response = await session.get(
                        f'https://psnprofiles.com{guide_link.a["href"]}'
                    )
                    await guide_response.html.arender()
                    await asyncio.sleep(0.1)
                    guide_soup = BeautifulSoup(guide_response.html.html, "lxml")

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

        # Chronologicall order
        new_platinums_banner.reverse()

        return new_platinums_banner

    async def update_psn_profile(self) -> None:
        """Updates the PSNProfile so that the latest trophy information can be extracted"""

        launch_options = {
            "headless": True,
        }

        # Adjust options for Raspberry Pi
        if running_in_raspberry_pi():
            launch_options.update(
                {
                    "executablePath": CHROMIUM_RASPBERRY_PATH,
                }
            )

        browser = await launch(**launch_options)
        page = await browser.newPage()

        await page.goto("https://psnprofiles.com/")

        # Find the text input field by id and type gamer tag
        await page.type("#psnId", self.gamer_tag)

        # CLick on the green "Update User" button
        await page.evaluate(
            """() => {
            document.querySelector("a.button.green[onclick*='updatePsnUser']").click();
        }"""
        )

        print(f"Updating {self.gamer_tag} profile, sleeping...")
        await asyncio.sleep(10)

        await browser.close()
