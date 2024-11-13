import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Set

from bs4 import BeautifulSoup
from pyppeteer import launch
from requests_html import HTMLSession

from .game import Console, Game
from .platinum import Platinum


@dataclass
class Player:
    """Represents a player"""

    gamer_tag: str

    games_with_platinum: Set[Game] = field(default_factory=set)

    def get_games_list(self):
        session = HTMLSession()
        response = session.get(f"https://psnprofiles.com/{self.gamer_tag}")
        response.html.render()

        soup = BeautifulSoup(response.html.html, "lxml")
        games_table = soup.find(id="gamesTable").tbody
        games_with_platinum = games_table.find_all("tr", class_="platinum")

        for game in games_with_platinum:

            tds = game.find_all("td")
            anchor = tds[1].div.span.a

            name = anchor.text
            game_id = anchor["href"].split("/")[2]
            console = Console[tds[2].span.div.span.text]

            date = tds[1].find_all("div")[-1].text.split("•")[0].strip()
            space_index = date.index(" ")
            date = datetime.strptime(
                date[: space_index - 2] + date[space_index:], "%d %B %Y"
            )

            game = Game(id=game_id, name=name, console=console)

            if game not in self.games_with_platinum:
                pass

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
