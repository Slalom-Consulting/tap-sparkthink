"""sparkthink Authentication."""
from __future__ import annotations
from singer_sdk.helpers._util import utc_now
import requests
import json
from singer_sdk.authenticators import OAuthAuthenticator, SingletonMeta


class sparkthinkAuthenticator(OAuthAuthenticator, metaclass=SingletonMeta):
    """Authenticator class for gapi."""

    @property
    def oauth_request_body(self) -> dict:
        """Define the OAuth request body for the AutomaticTestTap API.

        Returns:
            A dict with the request body
        """
        return {
            "clientSecret": self.config["client_secret"],
        }
    
    @property
    def auth_endpoint(self):
        return self.config['auth_endpoint'] + self.config['service_account_id']

    def update_access_token(self) -> None:
        """Update `access_token` along with: `last_refreshed` and `expires_in`.

        Raises:
            RuntimeError: When OAuth login fails.
        """
        request_time = utc_now()
        auth_request_payload = self.oauth_request_payload
        self._oauth_headers['Content-Type'] = 'application/json'
        token_response = requests.post(
            self.auth_endpoint,
            headers=self._oauth_headers,
            data=json.dumps(auth_request_payload),
            timeout=60,
        )
        try:
            token_response.raise_for_status()
        except requests.HTTPError as ex:
            msg = f"Failed OAuth login, response was '{token_response.json()}'. {ex}"
            raise RuntimeError(msg) from ex

        self.logger.info("OAuth authorization attempt was successful.")

        token_json = token_response.json()
        self.access_token = token_json["bearerToken"]
        expiration = token_json.get("expiresOn", self._default_expiration)
        self.expires_in = int(expiration) if expiration else None
        if self.expires_in is None:
            self.logger.debug(
                "No expires_in received in OAuth response and no "
                "default_expiration set. Token will be treated as if it never "
                "expires.",
            )
        self.last_refreshed = request_time
