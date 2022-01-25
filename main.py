import collections

import steamreviews
import requests
from typing import Collection
from time import sleep
from pathlib import Path
from datetime import datetime


def get_applist() -> object:
    """
    Get's all appids from the steam api and returns a dict with all of them
    :return:
    """
    applist_url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
    r = requests.get(applist_url)

    return r.json()["applist"]["apps"]


def check_if_game(app_id: str) -> bool:
    """
    Checks if a steam appid is a game
    :param app_id: Appid to check if is game
    :return: True if app is game
    """
    app_id = str(app_id)

    if not check_if_in_file(app_id) and not check_if_in_file(app_id, filename="processed_app_ids"):
        app_details_url = "https://store.steampowered.com/api/appdetails"
        params = {"appids": app_id}
        r = requests.get(app_details_url, params=params)

        if r.status_code == 200:
            data = r.json().get(app_id).get("data")
            if data:
                if data.get("type") == "game":
                    print(f"Finished checking {app_id}")
                    write_id_to_file(app_id)
                    return True
                else:
                    print(f"Not game. Writing app_id to file")
                    write_id_to_file(app_id, filename="processed_app_ids")
        else:
            print(f"Status code not 200. Sleeping for 300 seconds")
            sleep(300)
            check_if_game(app_id)
    else:
        print(f"{app_id} already processed. Skipping")


def write_id_to_file(id: str, filename: str = "game_ids") -> None:
    """
    Writes a game_id to a file. Default filename is processed_game_ids
    :param id: Game_id to write to file
    :param filename: Filename to write to
    :return: None
    """
    # timestamp = datetime.now().strftime("%Y_%m_%d-%HH:%MM:%S")
    file = Path(f"{filename}")
    with open(filename, "a+") as f:
        f.write(f"{id}\n")
        # f.write_text(game_id)


def check_if_in_file(game_id, filename: str = "processed_game_ids") -> bool:
    """
    Checks if a game_id is in file in order to avoid processing multiple times
    :param game_id: Game_id to check
    :param filename: Filename to look in
    :return: None
    """
    f = Path(filename)
    if f.exists():
        file_text = Path.read_text(f)
        return game_id in file_text
    else:
        return False


def main():
    """
    Returns review data for all games on the steam store
    :return:
    """
    app_ids = [app["appid"] for app in get_applist()]
    games = [app for app in app_ids if check_if_game(app)]

    steamreviews.download_reviews_for_app_id_batch(games)


if __name__ == '__main__':
    main()
