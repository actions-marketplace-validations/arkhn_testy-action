import requests
from typing import List, Optional

KNOWN_ZONES = ["fr-par-1"]


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
        return self.session.get(f"{self.base_url}/images").json()["images"]

    def find_image(self, name: str) -> Optional[dict]:
        images = self.list_images()
        for image in images:
            if image["name"] == "Ubuntu 18.04 Bionic Beaver":
                return image

        return None

    def create_server(
        self,
        name: str,
        image_id: str,
        project_id: str,
        commercial_type: Optional[str] = "DEV1-S",
    ) -> dict:
        data = {
            "name": name,
            "commercial_type": commercial_type,
            "image": image_id,
            "volumes": {},
            "project": project_id,
        }
        return self.session.post(f"{self.base_url}/servers", json=data).json()["server"]

    def perform_server_action(self, server_id: str, action: str):
        data = {"action": action}
        return self.session.post(
            f"{self.base_url}/servers/{server_id}/action", json=data
        ).json()

    def poweron_server(self, server_id):
        return self.perform_server_action(server_id, action="poweron")

    def poweroff_server(self, server_id):
        return self.perform_server_action(server_id, action="poweroff")

    def delete_server(self, server_id: str):
        return self.session.delete(f"{self.base_url}/servers/{server_id}")
