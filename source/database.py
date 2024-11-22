import os
import pickle

from classes.player import Player


class Database:
    """
    This class stores data related to the bot operation
    and acts as an interface in case it is upgraded to an actual database in the future
    """

    __BACKUP_FILE = "db.pkl"

    def __init__(self) -> None:

        self.__data: dict[str, Player] = dict()  # Key is the gamer tag

    def add_player(self, new_gamer_tag: Player):
        """Adds a player"""

        # Check if this player already exists
        if new_gamer_tag in self.__data:
            raise ValueError("This player is already being tracked.")

        player = Player(gamer_tag=new_gamer_tag)

        self.__data[new_gamer_tag] = player

        return player

    def remove_player(self, gamer_tag: str):
        """Removes a player"""

        if gamer_tag not in self.__data:
            raise ValueError("This player doesn't exist.")
        else:
            del self.__data[gamer_tag]

    def get_players_list(self) -> list[Player]:
        """Returns the list of players being tracked"""

        return list(self.__data.values())

    def save_backup(self):
        """Saves a backup of the database in a file"""

        with open(self.__BACKUP_FILE, "wb") as backup_file:
            pickle.dump(self.__data, backup_file)

    def try_load_backup(self):
        """Tries to load a backup of the database (returns a boolean representing whether it was successful or not)"""

        if os.path.exists(self.__BACKUP_FILE):
            with open(self.__BACKUP_FILE, "rb") as backup_file:
                self.__data = pickle.load(backup_file)
                return True
        else:
            return False
