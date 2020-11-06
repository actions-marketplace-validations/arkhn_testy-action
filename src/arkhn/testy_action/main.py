import argparse

from arkhn.testy_action.scaleway import APIClient


def build_args_parser() -> argparse.ArgumentParser:
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

    return parser


def provision_server(api: APIClient) -> dict:
    ubuntu_image = api.find_image(name="Ubuntu 18.04 Bionic Beaver")
    server = api.create_server(
        name="testy", image_id=ubuntu_image["id"], project_id=args.project_id
    )
    api.poweron_server(server["id"])

    return server


def withdraw_server(server: dict, api: APIClient) -> None:
    api.poweroff_server(server["id"])

    import time

    time.sleep(40)

    api.delete_server(server["id"])


def main():
    parser = build_args_parser()
    args = parser.parse_args()

    api = APIClient(auth_token=args.token)

    server = provision_server(api)

    import time

    time.sleep(20)

    withdraw_server(server, api)
