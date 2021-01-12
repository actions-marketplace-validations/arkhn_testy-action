import logging
import pprint
import time
from pathlib import Path

from arkhn.testy_action.args import parse_args
from arkhn.testy_action.deploy import deploy_stack, make_host_vars
from arkhn.testy_action.provision import APIClient, Image
from arkhn.testy_action.utils import KeyscanError, add_instance_to_known_hosts

logging.basicConfig()

logger = logging.getLogger(__file__)


def main():
    args = parse_args()

    api = APIClient(auth_token=args.token)

    with api.create_server(
        name=args.context_name,
        image=Image.UBUNTU,
        project_id=args.project_id,
        terminate=not args.debug,
    ) as server:
        logger.debug(pprint.pformat(server))

        api.poweron_server(server["id"])

        while (server := api.get_server(server["id"])) and server["state"] != "running":
            time.sleep(10)

        try:
            add_instance_to_known_hosts(
                Path("known_hosts"), server["public_ip"]["address"]
            )
        except KeyscanError:
            logger.error("Could not fetch instance fingerprints.")
            exit(1)

        ansible_return_code = deploy_stack(
            runner_dir=args.runner_dir,
            playbook_dir=args.playbook_dir,
            host_vars=make_host_vars(
                host=server["public_ip"]["address"],
                cloud_key_file=args.cloud_key,
                versions=args.versions,
            ),
        )
        exit(ansible_return_code)
