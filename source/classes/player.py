import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from io import BytesIO
from typing import Set

import requests
from bs4 import BeautifulSoup
from PIL import Image
from pyppeteer import launch
from requests_html import HTMLSession

from .game import Console, Game
from .platinum import Platinum


@dataclass
class Player:
    """Represents a player"""

    gamer_tag: str

    games_with_platinum: Set[Game] = field(default_factory=set)

    def get_new_platinums_banners(self) -> list:
        """Returns the banners of the newly achieved platinums"""

        new_platinums_banner = []

        # Load user profile page and render the games
        session = HTMLSession()
        response = session.get(f"https://psnprofiles.com/{self.gamer_tag}")
        response.html.render()

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
                response = session.get(
                    f"https://psnprofiles.com/trophies/{game.id}/{self.gamer_tag}"
                )
                response.html.render()
                game_trophies_soup = BeautifulSoup(response.html.html, "lxml")

                # Retrieve game banner
                banner_url = (
                    game_trophies_soup.find(id="first-banner")
                    .find_all("div")[-1]["style"]
                    .split("url(")[-1][:-1]
                )
                response = requests.get(banner_url)
                image_data = BytesIO(response.content)
                game.banner = Image.open(image_data)

                # Go to the guide page to get the platinum information
                guide_link = game_trophies_soup.find("div", class_="guide-page-info")

                platinum_hours = None
                platinum_playthroughs = None
                platinum_difficulty = None

                # If it has a guide, retrieve information
                if guide_link is not None:

                    response = session.get(
                        f'https://psnprofiles.com{guide_link.a["href"]}'
                    )
                    response.html.render()
                    guide_soup = BeautifulSoup(response.html.html, "lxml")

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

        return new_platinums_banner

    def update_psn_profile(self) -> None:
        """Updates the PSNProfile so that the latest trophy information can be extracted"""

        async def run_func():

            browser = await launch(headless=True)
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

            await asyncio.sleep(30)

            await browser.close()

        asyncio.run(run_func())
