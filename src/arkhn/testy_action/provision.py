import logging
import time
from contextlib import contextmanager
from enum import Enum
from typing import Iterator, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

logger = logging.getLogger(__name__)


class Image(Enum):
    UBUNTU = 0


def log_and_raise(resp: requests.Response, *args, **kwargs):
    try:
        resp.raise_for_status()
    except requests.HTTPError as err:
        logger.error(resp.json())
        raise err


class BaseAPIClient:
    def __init__(
        self, base_url: str, session: Optional[requests.Session] = None
    ) -> None:
        self.base_url = base_url
        self._session = session or requests.Session()
        adapter = HTTPAdapter(
            max_retries=Retry(
                total=3, backoff_factor=10, status_forcelist=[429, 500, 502, 503, 504]
            )
        )
        self._session.mount("http", adapter)
        self._session.hooks["response"] = [log_and_raise]


class APIClient(BaseAPIClient):
    base_url = "https://api.scaleway.com/instance/v1/zones"
    known_zones = ["fr-par-1"]
    image_mapping = {Image.UBUNTU: "Ubuntu 18.04 Bionic Beaver"}

    def __init__(
        self,
        auth_token: str,
        session: Optional[requests.Session] = None,
        zone: Optional[str] = known_zones[0],
    ):
        super().__init__(base_url=f"{APIClient.base_url}/{zone}/", session=session)
        self._session.headers.update({"X-Auth-Token": auth_token})

    def list_images(self) -> List[dict]:
        resp = self._session.get(f"{self.base_url}/images")
        return resp.json()["images"]

    def find_image(self, name: str) -> Optional[dict]:
        images = self.list_images()
        for image in images:
            if image["name"] == name:
                return image

        return None

    def _create_server(
        self,
        name: str,
        image: Image,
        project_id: str,
        commercial_type: Optional[str] = "DEV1-S",
    ) -> dict:
        ubuntu_image = self.find_image(name=self.image_mapping[image])

        data = {
            "name": name,
            "commercial_type": commercial_type,
            "image": ubuntu_image["id"],
            "volumes": {},
            "project": project_id,
        }
        resp = self._session.post(f"{self.base_url}/servers", json=data)
        return resp.json()["server"]

    @contextmanager
    def create_server(
        self,
        name: str,
        image: Image,
        project_id: str,
        commercial_type: Optional[str] = "DEV1-S",
    ) -> Iterator[dict]:
        server = self._create_server(
            name=name,
            image=image,
            project_id=project_id,
            commercial_type=commercial_type,
        )

        try:
            yield server
        finally:
            retry = 0
            while retry < 3:
                try:
                    self.terminate_server(server["id"])
                except requests.HTTPError as err:
                    if err.response.status_code == 400:
                        time.sleep(10 * 2 ** (retry - 1))  # 5, 10, 20, etc.
                        retry += 1
                        continue
                break

    def get_server(self, server_id: str):
        resp = self._session.get(f"{self.base_url}/servers/{server_id}")
        return resp.json()["server"]

    def perform_server_action(self, server_id: str, action: str, retry: int = 3):
        data = {"action": action}
        resp = self._session.post(
            f"{self.base_url}/servers/{server_id}/action", json=data
        )
        return resp.json()

    def poweron_server(self, server_id):
        return self.perform_server_action(server_id, action="poweron")

    def poweroff_server(self, server_id):
        return self.perform_server_action(server_id, action="poweroff")

    def terminate_server(self, server_id: str):
        return self.perform_server_action(server_id, action="terminate")

    def delete_server(self, server_id: str):
        resp = self._session.delete(f"{self.base_url}/servers/{server_id}")
        return resp.json()
