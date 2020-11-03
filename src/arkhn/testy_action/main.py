import argparse

from arkhn.testy_action.scaleway import APIClient


def main():
    parser = argparse.ArgumentParser(
        prog="testy-action",
        description="Run Arkhn's integration test suites on cloud platform.",
    )

    parser.add_argument(
        "token",
        metavar="token",
        type=str,
        help="API token to authenticate to target cloud platform",
    )
    parser.add_argument(
        "project_id",
        metavar="project-id",
        type=str,
        help="Project ID on the cloud platform",
    )

    args = parser.parse_args()

    api = APIClient(auth_token=args.token)

    ubuntu_image = api.find_image(name="Ubuntu 18.04 Bionic Beaver")

    testy_server = api.create_server(
        name="testy", image_id=ubuntu_image["id"], project_id=args.project_id
    )

    api.poweron_server(testy_server["id"])

    import time

    time.sleep(20)

    api.poweroff_server(testy_server["id"])

    time.sleep(20)

    api.delete_server(testy_server["id"])