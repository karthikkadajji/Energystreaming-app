import requests

class APIClient:
    def __init__(self, token):
        self.base_url = "https://ds.netztransparenz.de/api/v1"
        self.token = token

    def make_api_request(self, endpoint, method="GET", headers=None, data=None):
        url = f"{self.base_url}/{endpoint}"

        if not headers:
            headers = {}

        headers['Authorization'] = f'Bearer {self.token}'

        response = requests.request(method, url=url, headers=headers, data=data)
        return response
