from dataclasses import dataclass,field
import os
from typing import Any, ClassVar,Optional, Tuple
from influxdb_client.client.influxdb_client import InfluxDBClient

from influxdb_client.client.write_api import SYNCHRONOUS,WriteApi
from influxdb_client.client.write.point import Point



@dataclass
class DbManager:
    DEFAULT_ORG: ClassVar[str] = "admin"
    DEFAULT_URL: ClassVar[str] = "http://192.168.0.203:8086"
    DEFAULT_BUCKET:ClassVar[str]="proximity_sensor"
    TOKEN_ENV_VAR_NAME:ClassVar[str]="INFLUXDB_TOKEN"

    org:str=field(default=DEFAULT_ORG)
    token:str=field(default_factory=lambda:DbManager.get_token())
    url:str=DEFAULT_URL
    bucket:str=field(default=DEFAULT_BUCKET)

    client:Optional[InfluxDBClient]=field(default=None)
    write_api:Optional[WriteApi]=field(default=None)
    # Store the URL of your InfluxDB instance
    def set_client(self):
        client = InfluxDBClient(
            url=self.url,
            token=self.token,
            org=self.org
        )

       

        self.client=client


    def set_write_api(self):
        if(self.client is None):
            raise ValueError("Cannot get write api with no client instantiated, call set_client first!")
        write_api=self.client.write_api(write_options=SYNCHRONOUS)
        
        self.write_api=write_api


    def setup_for_write(self):
        """Wrapper method, gets ready for writing to db"""
        self.set_client()
        self.set_write_api()

    def write_point(self,measurement_name:str,tag:Tuple[str,str],field:Tuple[str,Any]):
        """Preconditions: setup already done"""
        assert self.write_api is not None, "setup_for_write must be called first"
        tag_key,tag_value=tag
        field_key,field_value=field
        point=Point(measurement_name).tag(tag_key,tag_value).field(field_key, field_value)
        self.write_api.write(bucket=self.bucket,org=self.org,record=point)

    def ensure_write_ready(self):
        if(self.client is not None and self.write_api is not None):
            return True
        return False

    def write(self,measurement_name:str,tag:Tuple[str,str],field:Tuple[str,Any]):
        if(not self.ensure_write_ready()):
            self.setup_for_write()
        self.write_point(measurement_name=measurement_name,tag=tag,field=field)

    

    @staticmethod
    def get_token() -> str:
        """Get token from environment variable."""
        token = os.environ.get(DbManager.TOKEN_ENV_VAR_NAME)
        if not token:
            raise ValueError(f"{DbManager.TOKEN_ENV_VAR_NAME} environment variable is not set")
        return token
