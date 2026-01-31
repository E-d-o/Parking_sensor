import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional

from dotenv import load_dotenv
from influxdb_client.client.influxdb_client import InfluxDBClient
from influxdb_client.client.write.point import Point
from influxdb_client.client.write_api import SYNCHRONOUS, WriteApi

load_dotenv()


@dataclass
class DbManager:
    org: str = field(default_factory=lambda: DbManager.get_env_variable("INFLUXDB_ORG"))
    token: str = field(
        default_factory=lambda: DbManager.get_env_variable("INFLUXDB_TOKEN")
    )
    url: str = field(default_factory=lambda: DbManager.get_env_variable("INFLUXDB_URL"))
    bucket: str = field(
        default_factory=lambda: DbManager.get_env_variable("INFLUXDB_BUCKET")
    )

    client: Optional[InfluxDBClient] = field(default=None)
    write_api: Optional[WriteApi] = field(default=None)

    # Store the URL of your InfluxDB instance
    def set_client(self):
        client = InfluxDBClient(url=self.url, token=self.token, org=self.org)

        self.client = client

    def set_write_api(self):
        if self.client is None:
            raise ValueError(
                "Cannot get write api with no client instantiated, call set_client first!"
            )
        write_api = self.client.write_api(write_options=SYNCHRONOUS)

        self.write_api = write_api

    def setup_for_write(self):
        """Wrapper method, gets ready for writing to db"""
        self.set_client()
        self.set_write_api()

    def write_point(
        self,
        measurement_name: str,
        tags: Dict[str, str],
        fields: Dict[str, float | int | bool | str],
        time: Optional[datetime | str] = None,
    ):
        """Write a point with multiple tags and fields."""
        assert self.write_api is not None, "setup_for_write must be called first"

        point = Point(measurement_name)
        for tag_key, tag_value in tags.items():
            point = point.tag(tag_key, str(tag_value))  # Tags sono sempre stringhe
        for field_key, field_value in fields.items():
            point = point.field(field_key, field_value)

        if time is not None:
            point = point.time(time)

        self.write_api.write(bucket=self.bucket, org=self.org, record=point)

    def ensure_write_ready(self):
        if self.client is not None and self.write_api is not None:
            return True
        return False

    def write(
        self,
        measurement_name: str,
        tags: Dict[str, str],
        fields: Dict[str, float | int | bool | str],
        time: Optional[datetime | str] = None,
    ):
        """Convenience method to ensure setup and write a point."""
        if not self.ensure_write_ready():
            self.setup_for_write()
        self.write_point(
            measurement_name=measurement_name, tags=tags, fields=fields, time=time
        )

    def close(self):
        if self.ensure_write_ready():
            assert self.write_api is not None, "write_api is none, cannot close"

            assert self.client is not None, "client is none, cannot close"

            self.write_api.close()
            self.client.close()

            print("Chiusa connessione con successo")
        else:
            raise Exception("Cannot close a connection which hasn't been opened")

    @staticmethod
    def get_env_variable(name: str) -> str:
        """Get token from environment variable."""
        env_var = os.getenv(name)
        if not env_var:
            raise ValueError(f"{name} environment variable is not set")
        return env_var
