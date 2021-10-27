"""GraphQL client handling, including sparkthinkStream base class."""

import requests
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable, cast

from singer_sdk.streams import GraphQLStream
from singer_sdk.helpers.jsonpath import extract_jsonpath

from tap_sparkthink.auth import sparkthinkAuthenticator

class sparkthinkStream(GraphQLStream):
    """sparkthink stream class."""

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return self.config["api_endpoint"]

    # Alternatively, use a static string for url_base:
    # url_base = "https://api.mysample.com"
    @property
    def authenticator(self) -> sparkthinkAuthenticator:
        """Return a new authenticator object."""
        return sparkthinkAuthenticator.create_for_stream(self)

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")
        return headers
    
    @property
    def response_batch_size(self) -> str:
        """Return the response_batch_size."""
        return self.config.get("response_batch_size")
    
    @property
    def response_default_batch_size(self) -> int:
        """Return the response_default_batch_size."""
        return 10

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        if response.json().get("errors"):
            self.logger.error(
                f"Received errors in raw query response: {response.json()}"
            )

        yield from extract_jsonpath(self.records_jsonpath, input=response.json())

class ProjectBasedStream(sparkthinkStream):
    """Base class for streams that are keyed based on project ID."""
    @property
    def partitions(self) -> List[dict]:
        """Return a list of partition key dicts (if applicable), otherwise None."""
        
        if "project" in self.records_jsonpath:
            return [
                {
                    "project_id": id,
                    "response_batch_size": self.response_batch_size or self.response_default_batch_size
                } 
                for id in [ x.strip() for x in self.config.get("project_ids").strip('[]').split(',') ]
            ]

        raise ValueError(
            "Could not detect partition type for stream "
            f"'{self.name}' ({self.records_jsonpath}). "
            "Expected a records_jsonpath containing 'project'. "
        )

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values for each query variable

        """
        if next_page_token:
            context['cursor'] = next_page_token
        
        return context or {}

    def post_process(self, row: dict, context: Optional[dict] = None) -> dict:
        """As needed, append or transform raw data to match expected structure."""
        if row is None:
            self.logger.warning(f"No data for project_id '{context['project_id']}'")
            return {} # handle bad/empty row (no data found based on given project_id)

        row['project_id'] = context['project_id'] 
                 
        return row
