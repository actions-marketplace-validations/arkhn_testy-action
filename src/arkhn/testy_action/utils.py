import logging
import subprocess
import time
from pathlib import Path

logger = logging.getLogger(__file__)


class KeyscanError(Exception):
    pass


def add_instance_to_known_hosts(known_hosts: Path, host: str) -> None:
    logger.debug("Scanning instance fingerprints")
    with open(known_hosts, "a+") as fd:
        retry = 0
        while retry < 5:
            keyscan = subprocess.run(
                ["ssh-keyscan", "-t", "rsa", host],
                stdout=subprocess.PIPE,
                check=True,
            )
            if "ssh-rsa" in str(keyscan.stdout):
                fd.write(str(keyscan.stdout))
                return
            time.sleep(10 * 2 ** retry)  # 10, 20, etc.
            retry += 1
        raise KeyscanError
