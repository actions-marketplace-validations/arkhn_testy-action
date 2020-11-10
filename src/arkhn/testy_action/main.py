import argparse
import uuid

from arkhn.testy_action.provision import APIClient, Image


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
    parser.add_argument(
        "--context-name",
        metavar="NAME",
        dest="context_name",
        default=None,
        type=str,
        help="Optional name for the context",
    )

    return parser


def main():
    parser = build_args_parser()
    args = parser.parse_args()

    token = args.token
    project_id = args.project_id
    context_name = args.context_name or str(uuid.uuid4())

    api = APIClient(auth_token=token)

    with api.create_server(
        name=context_name, image=Image.UBUNTU, project_id=project_id
    ) as server:
        server = api.poweron_server(server["id"])
