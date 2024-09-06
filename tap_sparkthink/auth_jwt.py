"""sparkthink Authentication."""


import requests
import logging
import backoff

from requests.adapters import HTTPAdapter, Retry
from singer_sdk.authenticators import OAuthJWTAuthenticator

from singer_sdk.helpers._util import utc_now

logging.basicConfig(level=logging.DEBUG)

class sparkthinkAuthenticator(OAuthJWTAuthenticator):
    """Authenticator class for sparkthink."""
    @classmethod
    def create_for_stream(cls, stream) -> "sparkthinkAuthenticator":
        
        return cls(
            stream=stream,
            # auth_endpoint = f"{cls.auth_endpoint_url}{cls.service_account_id}" 
            # oauth_scopes="TODO: OAuth Scopes",
        )

    @property
    def oauth_request_payload(self) -> dict:
        """Return request payload for OAuth request."""

        return  {
            "clientSecret": self.config['client_secret']
        } 
    
    # Authentication and refresh
    def update_access_token(self):
        """Update `access_token` along with: `last_refreshed` and `expires_in`."""
        request_time = utc_now()
        auth_endpoint = self.config['auth_endpoint'] + self.config['service_account_id']
        auth_request_payload = self.oauth_request_payload

        requests_session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[500,502,503,504])
        requests_session.mount('https://', HTTPAdapter(max_retries=retries))
        if not self.access_token:
            try:
                self.logger.info("Sending post request")
                token_response = requests_session.post(auth_endpoint, json=auth_request_payload) 
            except ConnectionError:
                self.logger.info("Error in token request")
        try:    
            token_response.raise_for_status()
            self.logger.info("OAuth authorization attempt was successful.")
        except Exception as ex:
            raise RuntimeError(
                f"Failed OAuth login, response was '{token_response.json()}'. {ex}"
            )
        token_json = token_response.json()
        # print(f'token_response: {token_response}, token_json: {token_json}')
        self.access_token = token_json["bearerToken"]
        self.expires_in = token_json["expiresOn"]
        self.last_refreshed = request_time
