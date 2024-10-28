from bs4 import BeautifulSoup
from requests_html import HTMLSession
from classes.game import Game
from classes.platinum import Platinum
from classes.player import Player

player = Player(gamer_tag = "DiogoMDSilva")
session = HTMLSession()
response = session.get(f'https://psnprofiles.com/{player.gamer_tag}')
response.html.render()

soup = BeautifulSoup(response.html.html, "lxml")
games_table = soup.find(id = "gamesTable").tbody
games_with_platinum = games_table.find_all("tr", class_= "platinum")

print(len(games_with_platinum))

