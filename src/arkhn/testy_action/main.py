import argparse

from arkhn.testy_action.scaleway import APIClient, Image


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


def provision_server(project_id: str, image: Image, api: APIClient) -> dict:
    server = api.create_server(name="testy", image=image, project_id=project_id)
    api.poweron_server(server["id"])

    return server


def main():
    parser = build_args_parser()
    args = parser.parse_args()

    api = APIClient(auth_token=args.token)

    server = provision_server(project_id=args.project_id, image=Image.UBUNTU, api=api)

    import time

    time.sleep(20)

    api.terminate_server(server["id"])
