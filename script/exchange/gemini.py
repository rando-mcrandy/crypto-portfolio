import requests
import json
import base64
import hmac
import hashlib
import datetime, time

class GeminiApi:
    '''
    Interact with Gemini Api to retrieve balances.
    https://docs.gemini.com/rest-api/
    '''

    def __init__(self):
        self._gemini_api_key = ""
        self._gemini_api_secret = "".encode()
        t = datetime.datetime.now()
        self.payload_nonce = int(time.mktime(t.timetuple())*1000)

    def run(self):
        balances = self._get_balances()
        earn_balances = self._get_earn_balances()
        print(f"balances\n{balances}")
        print(f"earn_balances\n{earn_balances}")

    def _get_balances(self):
        url = "https://api.gemini.com/v1/balances"
        request = "/v1/balances"
        return self._send_request(url, request).json()

    def _get_earn_balances(self):
        url = "https://api.gemini.com/v1/balances/earn"
        request = "/v1/balances/earn"
        return self._send_request(url, request).json()
        
    def _send_request(self, url, request):
        payload =  {"request": request, "nonce": str(self.payload_nonce)}
        self.payload_nonce += 1
        encoded_payload = json.dumps(payload).encode()
        b64 = base64.b64encode(encoded_payload)
        signature = hmac.new(self._gemini_api_secret, b64, hashlib.sha384).hexdigest()

        request_headers = {
            'Content-Type': "text/plain",
            'Content-Length': "0",
            'X-GEMINI-APIKEY': self._gemini_api_key,
            'X-GEMINI-PAYLOAD': b64,
            'X-GEMINI-SIGNATURE': signature,
            'Cache-Control': "no-cache"
            }

        return requests.post(url, headers=request_headers)
