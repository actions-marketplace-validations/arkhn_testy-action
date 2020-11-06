from enum import Enum
import requests
import time
from typing import List, Optional

KNOWN_ZONES = ["fr-par-1"]


class Image(Enum):
    UBUNTU = "Ubuntu 18.04 Bionic Beaver"


class APIClient:
    def __init__(
        self,
        auth_token: str,
        session: Optional[requests.Session] = None,
        zone: Optional[str] = KNOWN_ZONES[0],
    ):
        self.base_url = f"https://api.scaleway.com/instance/v1/zones/{zone}"
        self.session = session or requests.Session()
        self.session.headers.update({"X-Auth-Token": auth_token})

    def list_images(self) -> List[dict]:
        resp = self.session.get(f"{self.base_url}/images")
        resp.raise_for_status()
        return resp.json()["images"]

    def find_image(self, name: str) -> Optional[dict]:
        images = self.list_images()
        for image in images:
            if image["name"] == "Ubuntu 18.04 Bionic Beaver":
                return image

        return None

    def create_server(
        self,
        name: str,
        image: Image,
        project_id: str,
        commercial_type: Optional[str] = "DEV1-S",
    ) -> dict:
        ubuntu_image = self.find_image(name=image.value)

        data = {
            "name": name,
            "commercial_type": commercial_type,
            "image": ubuntu_image["id"],
            "volumes": {},
            "project": project_id,
        }
        resp = self.session.post(f"{self.base_url}/servers", json=data)
        resp.raise_for_status()
        return resp.json()["server"]

    def get_server(self, server_id: str):
        resp = self.session.get(f"{self.base_url}/servers/{server_id}")
        resp.raise_for_status()
        return resp.json()["server"]

    def perform_server_action(self, server_id: str, action: str, retry: int = 3):
        backoff = 5
        data = {"action": action}

        def _perform_server_action():
            resp = self.session.post(
                f"{self.base_url}/servers/{server_id}/action", json=data
            )
            resp.raise_for_status()
            return resp.json()

        while retry > 0:
            retry -= 1

            try:
                return _perform_server_action()
            except requests.HTTPError as err:
                if retry == 0:
                    raise err
                else:
                    backoff *= 2
                    time.sleep(backoff)
                    continue

    def poweron_server(self, server_id):
        return self.perform_server_action(server_id, action="poweron")

    def poweroff_server(self, server_id):
        return self.perform_server_action(server_id, action="poweroff")

    def terminate_server(self, server_id: str):
        return self.perform_server_action(server_id, action="terminate")

    def delete_server(self, server_id: str):
        resp = self.session.delete(f"{self.base_url}/servers/{server_id}")
        return resp.raise_for_status()
