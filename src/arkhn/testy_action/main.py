import os

from arkhn.testy_action.scaleway import APIClient

AUTH_TOKEN = os.environ["AUTH_TOKEN"]
PROJECT_ID = os.environ["PROJECT_ID"]


def main():
    api = APIClient(auth_token=AUTH_TOKEN)

    ubuntu_image = api.find_image(name="Ubuntu 18.04 Bionic Beaver")

    testy_server = api.create_server(
        name="testy", image_id=ubuntu_image["id"], project_id=PROJECT_ID
    )

    api.poweron_server(testy_server["id"])

    import time

    time.sleep(20)

    api.poweroff_server(testy_server["id"])

    time.sleep(20)

    api.delete_server(testy_server["id"])