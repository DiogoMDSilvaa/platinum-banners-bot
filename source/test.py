from bs4 import BeautifulSoup
from requests_html import HTMLSession
from classes.player import Player

player = Player(gamer_tag="DiogoMDSilva")

player.get_new_platinums_banners()
