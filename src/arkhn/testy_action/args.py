import argparse
import json
import logging
import uuid
from pathlib import Path

logger = logging.getLogger(__file__)


def random_default_id(value: str) -> str:
    value = value or str(uuid.uuid4())
    return value


def dir_path(value: str) -> Path:
    path = Path(value).resolve()
    if path.is_dir():
        return path
    else:
        raise argparse.ArgumentTypeError(f"{value} is not a directory")


def file_path(value: str) -> Path:
    path = Path(value).resolve()
    if path.is_file():
        return path
    else:
        raise argparse.ArgumentTypeError(f"{value} is not a file")


def json_object(value: str) -> dict:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as err:
        raise argparse.ArgumentTypeError(err)

    if not isinstance(parsed, dict):
        raise argparse.ArgumentTypeError("Not an json objet.")

    return parsed


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
        help="Project ID on the cloud platform.",
    )
    parser.add_argument(
        "cloud_key",
        metavar="cloud-key",
        type=file_path,
        help=("Path to the private ssh key to connect to the provisionned server."),
    )
    parser.add_argument(
        "docker_username",
        metavar="docker-username",
        type=str,
        help=("Username used to login to the Docker hub"),
    )
    parser.add_argument(
        "docker_password",
        metavar="docker-password",
        type=str,
        help=("Password used to login to the Docker hub"),
    )
    parser.add_argument(
        "--context-name",
        metavar="NAME",
        dest="context_name",
        default=None,
        type=random_default_id,
        help="Optional name for the context.",
    )
    playbook_dir_default = f"{Path.cwd() / 'project'}"
    parser.add_argument(
        "--playbook-dir",
        metavar="DIR",
        dest="playbook_dir",
        default=playbook_dir_default,
        type=dir_path,
        help=(
            "Optional path to the deployment playbook directory. "
            f"Defaults to {playbook_dir_default}."
        ),
    )
    runner_dir_default = f"{Path.cwd()}"
    parser.add_argument(
        "--runner-dir",
        metavar="DIR",
        dest="runner_dir",
        default=runner_dir_default,
        type=dir_path,
        help=f"Optional path for the runner output. Defaults to {runner_dir_default}",
    )
    parser.add_argument(
        "--versions",
        metavar="VERSIONS_MAP",
        default={},
        type=json_object,
        help="Optional versions mapping, to override a subset of the default versions.",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Keep provisionned server up."
    )
    parser.add_argument("--verbose", action="store_true", help="Increase verbosity.")

    return parser


def parse_args() -> argparse.Namespace:
    parser = build_args_parser()
    args = parser.parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    logger.debug(args)
    return args
