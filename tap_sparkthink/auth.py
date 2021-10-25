"""sparkthink Authentication."""


import requests
from singer_sdk.authenticators import OAuthJWTAuthenticator

from singer_sdk.helpers._util import utc_now

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
        token_response = requests.post(auth_endpoint, json=auth_request_payload) 
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
