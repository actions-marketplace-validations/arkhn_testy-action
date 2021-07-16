import logging
from pathlib import Path
from typing import Dict

import ansible_runner

logger = logging.getLogger(__file__)


def make_host_vars(
    host: str, cloud_key_file: Path, versions: Dict[str, str], **kwargs
) -> dict:
    versions_vars = {f"{k}_version": v for k, v in versions.items()}

    return {
        "ansible_host": host,
        "ansible_user": "root",
        "ansible_ssh_private_key_file": str(cloud_key_file),
        "extended_stack": False,
        "public_host": "localhost",
        "api_domain": "nginx",
        "use_ssl": False,
        "public_port": 8080,
        "env": "test",
        "postgres_root_user": "postgres",
        "postgres_root_password": "yeahsexiscoolbuthaveyoutriedpyrog?",
        **versions_vars,
        **kwargs,
    }


def deploy_stack(runner_dir: Path, playbook_dir: Path, host_vars: dict) -> int:
    inventory = {"all": {"hosts": {"test": host_vars}}}

    logger.debug(inventory)

    result: ansible_runner.Runner = ansible_runner.interface.run(
        playbook="play.yml",
        private_data_dir=str(runner_dir),
        project_dir=str(playbook_dir),
        inventory=inventory,
        extravars={"host_is_bounded": True},
        verbosity=2
    )
    return result.rc
