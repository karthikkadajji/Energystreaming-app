import requests
class AccessTokenHandler:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token_url = "https://identity.netztransparenz.de/users/connect/token"
        self.token = None

    def get_access_token(self):
        if not self.token:
            response = requests.post(self.access_token_url, data={
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret
            })

            if response.ok:
                self.token = response.json()['access_token']
            else:
                print(f'Error retrieving token\n{response.status_code}:{response.reason}')
                return None

        return self.token
