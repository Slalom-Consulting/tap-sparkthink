"""sparkthink tap class."""

from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th  # JSON schema typing helpers

# TODO: Import your custom stream types here:
from tap_sparkthink.streams import (
    sparkthinkStream,
    MyProjectsStream,
    ProjectStream,
    TeamMembersStream,
    RespondentsStream,
    ResponsesStream,
    QuestionsStream,
)
# TODO: Compile a list of custom stream types here
#       OR rewrite discover_streams() below with your custom logic.
STREAM_TYPES = [
    MyProjectsStream,
    ProjectStream,
    TeamMembersStream,
    RespondentsStream,
    ResponsesStream,
    QuestionsStream,
]


class Tapsparkthink(Tap):
    """sparkthink tap class."""
    name = "tap-sparkthink"

    config_jsonschema = th.PropertiesList(
        th.Property("auth_endpoint", th.StringType, required=True),
        th.Property("api_endpoint", th.StringType, required=True),
        th.Property("service_account_id", th.StringType, required=True),
        th.Property("client_secret", th.StringType, required=True),
        th.Property("project_ids", th.StringType, required=True),
        th.Property("response_batch_size", th.IntegerType, required=False),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
